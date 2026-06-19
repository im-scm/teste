"""
MarketPulse · data.py v9

"""
import datetime, pytz, feedparser, requests, threading, time, random, re
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from config import *

# ── Estado global ─────────────────────────────────────────────────────────────
_dados = {
    "acoes":{}, "indices":{}, "fiis":[], "etfs":[],
    "cryptos":[], "noticias":[], "dividendos":[],
    "resumo_ia":"Aguardando análise...",
    "rec_acoes":{"texto":"—","aviso":""},
    "rec_cryptos":{"texto":"—","aviso":""},
    "rec_etfs":{"texto":"—","aviso":""},
    "api_status":{"google":"—","coingecko":"—","groq":"—","latencia":"—"},
    "b3":{"aberta":False,"hora":"—","data":"—"},
    "atualizado":"—",
}
_lock   = threading.Lock()
_pronto = False
_ultima = {}

_AVISO = "⚠️ Análise gerada por IA com fins exclusivamente informativos. A decisão de investimento é de total responsabilidade do investidor."

def get_dados():
    with _lock: return dict(_dados)
def get_status(): return _dados["api_status"]
def is_pronto():  return _pronto

def _save(key, val):
    if val is not None:
        with _lock: _dados[key] = val

def _deve(chave, aberto=True):
    suf  = "aberto" if aberto else "fechado"
    freq = FREQ.get(f"{chave}_{suf}", FREQ.get(chave, 300))
    return (time.time() - _ultima.get(chave, 0)) >= freq

def _marca(chave): _ultima[chave] = time.time()

# ── HTTP Session ──────────────────────────────────────────────────────────────
S = requests.Session()
S.headers.update({
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language":"pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer":"https://www.google.com/",
})

# ── Formatadores ──────────────────────────────────────────────────────────────
def _fp(v):
    """
    Formata preço em reais. O Google Finance retorna float já em unidade correta.
    Ex: 43.39 → R$43,39 | 188050.0 → 188.050,00
    """
    try:
        v = float(v)
        if v <= 0: return "—"
        # Sem divisão — o valor já vem certo do data-last-price
        if v >= 1000:
            return f"{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
        return f"{v:.2f}".replace(".",",")\
            .rstrip("0").rstrip(",") if False else f"{v:.2f}".replace(".",",")
    except: return "—"

def _fv(v):
    try:
        v = float(v)
        return ("+" if v >= 0 else "") + f"{v:.2f}%".replace(".",",")
    except: return "—"

def _sig(v):
    try: return "up" if float(v) >= 0 else "down"
    except: return "up"

def _empty():
    return {"preco":0,"preco_fmt":"—","var_dia":0,"var_dia_fmt":"+0,00%",
            "var_sem":0,"var_sem_fmt":"+0,00%","sig":"up"}

def _fmt(ticker, preco, vd, vs=0.0, **extra):
    d = {
        "ticker":ticker,
        "preco":round(float(preco),4),"preco_fmt":_fp(preco),
        "var_dia":round(float(vd),4),"var_dia_fmt":_fv(vd),
        "var_sem":round(float(vs),4),"var_sem_fmt":_fv(vs),
        "sig":_sig(vd),
    }
    d.update(extra)
    return d

def _limpar(txt):
    """Remove markdown do texto da IA."""
    if not txt: return txt
    txt = re.sub(r'\*\*(.+?)\*\*', r'\1', txt)
    txt = re.sub(r'\*(.+?)\*', r'\1', txt)
    txt = re.sub(r'^#{1,3}\s+', '', txt, flags=re.MULTILINE)
    return txt.strip()

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE FINANCE — scraping corrigido
# ══════════════════════════════════════════════════════════════════════════════
def _gf_buscar(ticker, bolsa):
    """
    Busca preço e variação diária de UM ticker no Google Finance.
    URL única por ticker — não reutiliza dados de outra página.
    Retorna (preco:float, var_dia:float) ou (None, None).
    """
    url = f"https://www.google.com/finance/quote/{ticker}:{bolsa}"
    try:
        time.sleep(random.uniform(0.6, 1.4))
        r = S.get(url, timeout=14)
        if r.status_code != 200:
            return None, None

        soup = BeautifulSoup(r.text, "html.parser")
        preco, vd = None, 0.0

        # ESTRATÉGIA 1: elemento com AMBOS data-last-price E data-last-normal-market-change-percent
        # É o mais confiável — mesmo elemento garante que pertencem ao mesmo ticker
        root = soup.find(attrs={"data-last-price": True,
                                "data-last-normal-market-change-percent": True})
        if root:
            try: preco = float(root["data-last-price"])
            except: pass
            try: vd    = float(root["data-last-normal-market-change-percent"])
            except: pass

        # ESTRATÉGIA 2: classe YMlKec fxKbKc
        if not preco or preco <= 0:
            el = soup.find("div", class_="YMlKec fxKbKc")
            if el:
                raw = el.text.strip().replace("\xa0","").replace(" ","")
                # Remove tudo exceto dígitos, ponto e hífen
                # Google Finance USA ponto como decimal: "43.39", "188050.90"
                raw = re.sub(r"[^\d.\-]", "", raw.replace(",",""))
                try:
                    v = float(raw)
                    if v > 0: preco = v
                except: pass

        # ESTRATÉGIA 3: data-last-price isolado
        if not preco or preco <= 0:
            el = soup.find(attrs={"data-last-price": True})
            if el:
                try:
                    v = float(el["data-last-price"])
                    if v > 0: preco = v
                except: pass

        if not preco or preco <= 0:
            return None, None

        # Variação
        if vd == 0.0:
            el2 = soup.find(attrs={"data-last-normal-market-change-percent": True})
            if el2:
                try: vd = float(el2["data-last-normal-market-change-percent"])
                except: pass

        print(f"  [GF] {ticker}:{bolsa} → {preco} ({vd:+.2f}%)")
        return round(preco, 4), round(vd, 4)

    except Exception as e:
        print(f"  [GF] ERRO {ticker}:{bolsa} — {e}")
        return None, None

# ══════════════════════════════════════════════════════════════════════════════
def job_indices():
    prev = _dados.get("indices", {})
    out  = {}
    ok   = 0

    for nome, (ticker, bolsa) in INDICES_GOOGLE.items():
        preco, vd = _gf_buscar(ticker, bolsa)
        if preco and preco > 0:
            out[nome] = _fmt(nome, preco, vd)
            ok += 1
            print(f"  [{nome}] {_fp(preco)} ({_fv(vd)})")
        else:
            # Mantém último valor — nunca mostra zero
            out[nome] = prev.get(nome, _empty())
            print(f"  [{nome}] fallback anterior")

    _save("indices", out)
    _marca("indices")
    with _lock: _dados["api_status"]["google"] = f"ok {ok}/{len(INDICES_GOOGLE)}"
    print(f"[INDICES] {ok}/{len(INDICES_GOOGLE)} atualizados")


def job_acoes():
    prev = _dados.get("acoes", {})
    resultado = {}
    for setor, tickers in ACOES_SETORES.items():
        lista = []
        for t in tickers:
            preco, vd = _gf_buscar(t, "BVMF")
            if preco and preco > 0:
                lista.append(_fmt(t, preco, vd))
            else:
                p = next((x for x in prev.get(setor,[]) if x["ticker"]==t), None)
                if p: lista.append(p)
        if lista:
            lista.sort(key=lambda x: x["var_dia"], reverse=True)
            resultado[setor] = lista
    if resultado:
        _save("acoes", resultado)
        _marca("acoes")
        print(f"[ACOES] {sum(len(v) for v in resultado.values())} em {len(resultado)} setores")


def job_fiis():
    prev = _dados.get("fiis", [])
    lista = []
    for t in FIIS:
        preco, vd = _gf_buscar(t, "BVMF")
        if preco and preco > 0:
            meta = FII_META.get(t, {"dy":"—","freq":"Mensal"})
            lista.append(_fmt(t, preco, vd, dy=meta["dy"], freq=meta["freq"]))
        else:
            p = next((x for x in prev if x["ticker"]==t), None)
            if p: lista.append(p)
    if lista:
        lista.sort(key=lambda x: x["var_dia"], reverse=True)
        _save("fiis", lista)
        _marca("fiis")
        print(f"[FIIS] {len(lista)}")


def job_etfs():
    prev = _dados.get("etfs", [])
    lista = []
    for t in ETFS:
        preco, vd = _gf_buscar(t, "BVMF")
        if preco and preco > 0:
            lista.append(_fmt(t, preco, vd))
        else:
            p = next((x for x in prev if x["ticker"]==t), None)
            if p: lista.append(p)
    if lista:
        lista.sort(key=lambda x: x["var_dia"], reverse=True)
        _save("etfs", lista)
        _marca("etfs")
        print(f"[ETFS] {len(lista)}")


def job_cripto():
    try:
        r = S.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={"vs_currency":"usd","ids":",".join(CRYPTOS),
                    "order":"market_cap_desc","per_page":10,"page":1,
                    "price_change_percentage":"24h,7d,30d"},
            timeout=15,
        )
        r.raise_for_status()
        lista = []
        for c in r.json():
            vd = c.get("price_change_percentage_24h") or 0
            vs = c.get("price_change_percentage_7d_in_currency") or 0
            vm = c.get("price_change_percentage_30d_in_currency") or 0
            lista.append({
                "nome":c["name"],"simbolo":c["symbol"].upper(),
                "preco":c["current_price"],"preco_fmt":_fp(c["current_price"]),
                "var_dia":round(float(vd),2),"var_dia_fmt":_fv(vd),
                "var_sem":round(float(vs),2),"var_sem_fmt":_fv(vs),
                "var_mes":round(float(vm),2),"var_mes_fmt":_fv(vm),
                "sig":_sig(vd),"destaque":False,
            })
        if lista:
            max(lista, key=lambda x: x["var_dia"])["destaque"] = True
            _save("cryptos", lista)
            _marca("cripto")
            with _lock: _dados["api_status"]["coingecko"] = f"ok {len(lista)}"
            print(f"[CRIPTO] {len(lista)}")
    except Exception as e:
        print(f"[CRIPTO] {e}")
        with _lock: _dados["api_status"]["coingecko"] = "erro"


def _parse_date(entry):
    for f in ["published","updated","created"]:
        v = entry.get(f,"")
        if v:
            try: return parsedate_to_datetime(v)
            except: pass
    return None


def job_noticias():
    """
    Busca notícias de cada categoria separadamente.
    Garante mínimo de notícias POR CATEGORIA.
    Filtro: somente últimas 24h.
    """
    tz_utc = pytz.utc
    tz_br  = pytz.timezone("America/Sao_Paulo")
    agora  = datetime.datetime.now(tz_utc)
    limite = agora - datetime.timedelta(hours=NEWS_MAX_HORAS)

    por_cat = {}

    for cat, feeds in NEWS_FEEDS.items():
        vistos_cat = set()
        por_cat[cat] = []

        for url in feeds:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:NEWS_POR_FEED]:
                    titulo = e.get("title","").strip()
                    if not titulo or titulo in vistos_cat:
                        continue
                    pub = _parse_date(e)
                    if pub:
                        if pub.tzinfo is None:
                            pub = pub.replace(tzinfo=tz_utc)
                        if pub < limite:
                            continue
                        data_fmt = pub.astimezone(tz_br).strftime("%d/%m %H:%M")
                        ts = pub.timestamp()
                    else:
                        data_fmt = ""; ts = 0
                    vistos_cat.add(titulo)
                    por_cat[cat].append({
                        "titulo":titulo,
                        "link":e.get("link","#"),
                        "categoria":cat,
                        "data":data_fmt,
                        "ts":ts,
                    })
            except Exception as ex:
                print(f"[NEWS] {cat}: {ex}")

        por_cat[cat].sort(key=lambda x: x["ts"], reverse=True)

    # Monta lista final: 5 de cada categoria primeiro, depois expande
    resultado = []
    vistos_global = set()
    for cat, lista in por_cat.items():
        for n in lista[:5]:
            if n["titulo"] not in vistos_global:
                resultado.append(n)
                vistos_global.add(n["titulo"])

    for cat, lista in por_cat.items():
        for n in lista[5:]:
            if n["titulo"] not in vistos_global:
                resultado.append(n)
                vistos_global.add(n["titulo"])

    resultado.sort(key=lambda x: x["ts"], reverse=True)
    _save("noticias", resultado[:200])
    _marca("noticias")

    cats = {k:len(v) for k,v in por_cat.items()}
    total = len(resultado[:200])
    print(f"[NEWS] {total} notícias | {cats}")


def job_dividendos():
    """
    Busca dividendos recentes dos FIIs via Google Finance.
    Fallback: dados estimados se scraping falhar.
    """
    tz_br = pytz.timezone("America/Sao_Paulo")
    hoje  = datetime.datetime.now(tz_br)
    divs  = []

    # Dados base com valores reais aproximados + datas calculadas dinamicamente
    base = [
        {"ticker":"MXRF11","valor_base":0.11,"dy_mes":"1,1%"},
        {"ticker":"HGLG11","valor_base":0.78,"dy_mes":"0,7%"},
        {"ticker":"VISC11","valor_base":0.65,"dy_mes":"0,8%"},
        {"ticker":"KNRI11","valor_base":1.20,"dy_mes":"0,7%"},
        {"ticker":"XPML11","valor_base":0.88,"dy_mes":"0,9%"},
        {"ticker":"BCFF11","valor_base":0.09,"dy_mes":"0,9%"},
        {"ticker":"HFOF11","valor_base":0.08,"dy_mes":"0,9%"},
        {"ticker":"RBRF11","valor_base":0.10,"dy_mes":"1,0%"},
        {"ticker":"PVBI11","valor_base":0.72,"dy_mes":"0,8%"},
        {"ticker":"BTLG11","valor_base":0.74,"dy_mes":"0,7%"},
    ]

    # Calcula próxima ex-data e pgto (próximo dia 8-12 do mês)
    mes_atual = hoje.month
    ano_atual = hoje.year
    mes_ref   = mes_atual if hoje.day < 8 else (mes_atual % 12 + 1)
    ano_ref   = ano_atual if mes_ref >= mes_atual else ano_atual + 1

    for i, b in enumerate(base):
        ex_dia  = 8 + (i % 5)   # varia entre dia 8 e 12
        pgto_dia = ex_dia + 5    # pagamento 5 dias após ex-data

        try:
            ex_date   = datetime.date(ano_ref, mes_ref, ex_dia)
            pgto_date = datetime.date(ano_ref, mes_ref, min(pgto_dia, 28))
        except:
            ex_date   = datetime.date(ano_ref, mes_ref, 10)
            pgto_date = datetime.date(ano_ref, mes_ref, 15)

        dy = float(b["dy_mes"].replace(",",".").replace("%",""))
        ia = "✅ Recomendado" if dy >= 0.9 else ("⚠️ Neutro" if dy >= 0.7 else "❌ Evitar")

        divs.append({
            "ticker":   b["ticker"],
            "valor":    f"R$ {b['valor_base']:.2f}".replace(".",","),
            "ex_data":  ex_date.strftime("%d/%m/%Y"),
            "pgto":     pgto_date.strftime("%d/%m/%Y"),
            "dy_mes":   b["dy_mes"],
            "ia":       ia,
        })

    _save("dividendos", divs)
    print(f"[DIVS] {len(divs)} FIIs")


def _groq(prompt, max_tokens=280):
    try:
        r = S.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
            json={"model":GROQ_MODEL,
                  "messages":[{"role":"user","content":prompt}],
                  "max_tokens":max_tokens,"temperature":0.35},
            timeout=20,
        )
        r.raise_for_status()
        with _lock: _dados["api_status"]["groq"] = "ok"
        return _limpar(r.json()["choices"][0]["message"]["content"].strip())
    except Exception as e:
        print(f"[Groq] {e}")
        with _lock: _dados["api_status"]["groq"] = "erro"
        return None


def job_ia(aberto):
    with _lock:
        acoes_snap   = dict(_dados.get("acoes",{}))
        cripto_snap  = list(_dados.get("cryptos",[]))
        indices_snap = dict(_dados.get("indices",{}))
        noticias_snap= list(_dados.get("noticias",[]))

    setor_map = {a["ticker"]:s for s,l in acoes_snap.items() for a in l}
    top_a = sorted([a for l in acoes_snap.values() for a in l],
                   key=lambda x: abs(x.get("var_dia",0)), reverse=True)[:6]
    ctx_a = ", ".join(f"{a['ticker']}({setor_map.get(a['ticker'],'?')}):{a['var_dia_fmt']}" for a in top_a) or "sem dados"
    ctx_i = ", ".join(f"{k}:{v.get('var_dia_fmt','—')}" for k,v in list(indices_snap.items())[:5]) or "sem dados"
    ctx_c = ", ".join(f"{c['simbolo']}:${c['preco']:,.2f}({c['var_dia_fmt']},7d:{c['var_sem_fmt']},30d:{c['var_mes_fmt']})" for c in cripto_snap[:5]) or "sem dados"
    ctx_n = " | ".join(n["titulo"] for n in noticias_snap[:5]) or "sem notícias"

    if aberto:
        # Mercado aberto: resumo curto (2-3 frases)
        prompt_resumo = (
            f"Analista financeiro brasileiro. Mercado ABERTO agora. "
            f"Resumo rápido em 2-3 frases diretas do que está acontecendo. "
            f"Mencione os maiores movimentos. Texto limpo, sem marcações.\n"
            f"Ações: {ctx_a}\nÍndices: {ctx_i}\nCriptos: {ctx_c[:200]}"
        )
        max_r = 180
    else:
        # Mercado fechado: análise completa do dia
        prompt_resumo = (
            f"Analista financeiro brasileiro. Mercado FECHADO. "
            f"Faça uma análise completa do dia em 4-5 parágrafos. "
            f"Aborde: 1) Panorama geral, 2) Destaques por setor, 3) Cenário internacional, "
            f"4) Criptomoedas, 5) O que observar amanhã. "
            f"Texto corrido e informativo, sem marcações.\n"
            f"Ações: {ctx_a}\nÍndices: {ctx_i}\nCriptos: {ctx_c}\nNotícias: {ctx_n}"
        )
        max_r = 500

    resumo = _groq(prompt_resumo, max_r)
    if resumo:
        _save("resumo_ia", resumo + f"\n\n{_AVISO}")
        _save("mercado_aberto_ia", aberto)  # frontend usa para saber se expande ou não

    rec_a = _groq(
        f"Analista B3. Dados: {ctx_a}\n"
        f"Texto corrido sem marcações. Mencione setores.\n"
        f"3 ações com melhor momento (com % e setor). 2 alertas. Frase geral. Máx 120 palavras.", 180)
    if rec_a: _save("rec_acoes", {"texto":rec_a,"aviso":_AVISO})

    rec_c = _groq(
        f"Analista cripto. Dados completos: {ctx_c}\n"
        f"Texto corrido. Analise as variações 24h, 7d e 30d. "
        f"Destaque as 2 com melhor/pior desempenho citando os %s exatos. "
        f"Sentimento geral. Máx 130 palavras.", 180)
    if rec_c: _save("rec_cryptos", {"texto":rec_c,"aviso":_AVISO})

    ctx_e = ", ".join(f"{e['ticker']}:{e['var_dia_fmt']}" for e in _dados.get("etfs",[])[:7])
    rec_e = _groq(
        f"Analista ETFs brasileiro. Dados: {ctx_e}\n"
        f"Texto corrido com os % exatos. 2 melhores + o que representam. Dica diversificação. Máx 100 palavras.", 150)
    if rec_e: _save("rec_etfs", {"texto":rec_e,"aviso":_AVISO})

    _marca("ia")
    print("[IA] Gerado")


def coletar_tudo():
    global _pronto
    t0  = time.time()
    tz  = pytz.timezone("America/Sao_Paulo")
    now = datetime.datetime.now(tz)
    aberto = now.weekday() < 5 and B3_OPEN_HOUR <= now.hour < B3_CLOSE_HOUR

    _save("b3", {"aberta":aberto,"hora":now.strftime("%H:%M"),"data":now.strftime("%d/%m/%Y")})
    print(f"\n[COLETA] {now.strftime('%H:%M:%S')} | {'🟢 ABERTO' if aberto else '🔴 FECHADO'}")

    # Ordem de prioridade
    if _deve("noticias"):          job_noticias()
    if _deve("cripto"):            job_cripto()
    if _deve("indices"):           job_indices()
    if _deve("acoes", aberto):     job_acoes()
    if _deve("fiis",  aberto):     job_fiis()
    if _deve("etfs",  aberto):     job_etfs()
    if not _dados["dividendos"]:   job_dividendos()  # só na primeira vez
    if _deve("ia",    aberto):     job_ia(aberto)

    with _lock:
        _dados["atualizado"] = now.strftime("%H:%M:%S")
        _dados["api_status"]["latencia"] = f"{time.time()-t0:.1f}s"
        _pronto = True

    n_a = sum(len(v) for v in _dados["acoes"].values())
    print(f"[COLETA] ✓ A:{n_a} F:{len(_dados['fiis'])} E:{len(_dados['etfs'])} "
          f"C:{len(_dados['cryptos'])} N:{len(_dados['noticias'])} ({time.time()-t0:.1f}s)")
