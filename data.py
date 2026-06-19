import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
BRAPI_TOKEN  = os.getenv("BRAPI_TOKEN", "")

B3_OPEN_HOUR  = 10
B3_CLOSE_HOUR = 18

# Frequências de coleta (segundos) — ajustadas conforme solicitado
FREQ = {
    "indices":         60,          # índices: 1 minuto
    "acoes_aberto":    30 * 60,     # ações: 30 min quando aberto
    "acoes_fechado":   4 * 60 * 60, # ações: 4h quando fechado
    "fiis_aberto":     30 * 60,     # FIIs: 30 min quando aberto
    "fiis_fechado":    4 * 60 * 60,
    "etfs_aberto":     30 * 60,     # ETFs: 30 min quando aberto
    "etfs_fechado":    4 * 60 * 60,
    "cripto":          5 * 60,      # cripto: 5 minutos
    "noticias":        10 * 60,     # notícias: 10 minutos
    "ia_aberto":       30 * 60,     # IA: 30 min quando aberto
    "ia_fechado":      6 * 60 * 60, # IA: 6h quando fechado
}

ACOES_SETORES = {
    "Energia":    ["PETR4","PRIO3","CSAN3","UGPA3","RRRP3"],
    "Bancos":     ["ITUB4","BBDC4","BBAS3","SANB11","BPAC11"],
    "Varejo":     ["MGLU3","LREN3","SOMA3","AZZA3","SBFG3"],
    "Telecom":    ["VIVT3","TIMS3"],
    "Mineração":  ["VALE3","CSNA3","GGBR4","USIM5"],
    "Utilidades": ["ELET3","CMIG4","SBSP3","CPLE6"],
}

FIIS = ["MXRF11","HGLG11","VISC11","KNRI11","XPML11",
        "BCFF11","HFOF11","RBRF11","PVBI11","BTLG11"]

ETFS = ["BOVA11","SMAL11","IVVB11","HASH11","DIVO11","FIND11","SPXI11"]

# Google Finance: (ticker, bolsa) — cada um diferente para não repetir
INDICES_GOOGLE = {
    "Ibovespa":   ("IBOV",   "INDEXBVMF"),
    "S&P 500":    ("SPX",    "INDEXSP"),
    "Nasdaq":     ("COMP",   "INDEXNASDAQ"),
    "Dólar/Real": ("USDBRL", "CURRENCY"),
    "Euro/Real":  ("EURBRL", "CURRENCY"),
    "Ouro":       ("XAUUSD", "CURRENCY"),
    "Petróleo":   ("USOIL",  "NYSE"),
}

CRYPTOS = [
    "bitcoin","ethereum","binancecoin","solana","ripple",
    "cardano","avalanche-2","dogecoin","polkadot","chainlink",
]

FII_META = {
    "MXRF11":{"dy":"12,8%","freq":"Mensal"},"HGLG11":{"dy":"8,4%","freq":"Mensal"},
    "VISC11":{"dy":"9,2%","freq":"Mensal"}, "KNRI11":{"dy":"8,1%","freq":"Mensal"},
    "XPML11":{"dy":"10,5%","freq":"Mensal"},"BCFF11":{"dy":"11,2%","freq":"Mensal"},
    "HFOF11":{"dy":"10,8%","freq":"Mensal"},"RBRF11":{"dy":"12,1%","freq":"Mensal"},
    "PVBI11":{"dy":"9,6%","freq":"Mensal"}, "BTLG11":{"dy":"9,0%","freq":"Mensal"},
}

NEWS_MAX_HORAS = 24   # só notícias das últimas 24h
NEWS_POR_FEED  = 20

NEWS_FEEDS = {
    "Brasil": [
        "https://news.google.com/rss/search?q=economia+brasil+mercado+financeiro&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=bolsa+ibovespa+b3+acoes+hoje&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=selic+banco+central+inflacao+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=petrobras+vale+itau+bradesco+resultados&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=mercado+financeiro+brasileiro+hoje&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    ],
    "EUA": [
        "https://news.google.com/rss/search?q=federal+reserve+juros+economia+americana&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=trump+tarifas+wall+street+nasdaq&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=sp500+mercado+americano+dow+jones&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=us+economy+recession+inflation+2026&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=trump+tariffs+economy+market+2026&hl=en&gl=US&ceid=US:en",
    ],
    "China": [
        "https://news.google.com/rss/search?q=china+economia+yuan+guerra+comercial&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=china+tarifas+trump+exportacao&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=china+economy+trade+war+2026&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=china+markets+stocks+economy+today&hl=en&gl=US&ceid=US:en",
    ],
    "Europa": [
        "https://news.google.com/rss/search?q=europa+BCE+euro+economia+juros&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=ucrania+russia+guerra+europa+energia&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=europe+economy+ECB+recession+2026&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=european+markets+today+economy&hl=en&gl=US&ceid=US:en",
    ],
    "Guerras": [
        "https://news.google.com/rss/search?q=guerra+oriente+medio+israel+iran+petroleo&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=russia+ucrania+guerra+sancoes+economia&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=guerra+comercial+tarifas+impacto+mercado&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=middle+east+war+oil+economy+2026&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=geopolitics+conflict+war+market+impact&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=iran+trump+war+oil+prices+2026&hl=en&gl=US&ceid=US:en",
    ],
    "Cripto": [
        "https://news.google.com/rss/search?q=bitcoin+ethereum+criptomoeda+mercado&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=bitcoin+price+crypto+market+2026&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=ethereum+solana+altcoin+crypto+news&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=crypto+regulation+blockchain+defi&hl=en&gl=US&ceid=US:en",
    ],
    "Mercado": [
        "https://news.google.com/rss/search?q=petroleo+commodities+ouro+dolar+mercado&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=investimento+dividendos+acoes+fii+etf&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "https://news.google.com/rss/search?q=oil+gold+commodities+market+today&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=global+markets+stocks+bonds+2026&hl=en&gl=US&ceid=US:en",
    ],
}
