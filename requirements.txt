# 📊 MarketPulse

> Painel financeiro brasileiro em tempo real — Ações B3, FIIs, ETFs, Criptomoedas e Notícias com análise de IA.

> 🚧 **Desenvolvimento temporariamente pausado.** O projeto está funcional e será retomado em breve com novas funcionalidades.

---

## 🚀 O que é

MarketPulse é um painel financeiro desktop construído com Python e Flask que agrega dados de múltiplas fontes gratuitas e entrega ao investidor brasileiro uma visão consolidada do mercado, sem precisar abrir 10 abas diferentes.

Desenvolvido como projeto pessoal e de portfólio, com foco em dados reais, automação inteligente e interface limpa.

---

## ✅ Funcionalidades

### 📈 Ações B3
- 25 ações organizadas por setor: Energia, Bancos, Varejo, Telecom, Mineração, Utilidades
- Variação diária em tempo real
- Ordenação automática por maior variação dentro de cada setor
- Sistema de Favoritos salvo no navegador
- Destaque visual: verde = alta, vermelho = queda

### 🏢 Fundos Imobiliários (FIIs)
- 10 FIIs monitorados: MXRF11, HGLG11, VISC11, KNRI11, XPML11 e mais
- Preço atual, variação do dia e Dividend Yield anual
- Frequência de pagamento por fundo

### 💰 Dividendos
- Calendário dinâmico com próximas ex-datas e datas de pagamento
- Valor estimado por cota
- Avaliação automática: Recomendado / Neutro / Evitar

### ₿ Criptomoedas
- Top 10 por market cap
- Variação em 24h, 7 dias e 30 dias
- Destaque 🔥 na cripto com maior alta do dia

### 📊 ETFs
- 7 ETFs brasileiros: BOVA11, SMAL11, IVVB11, HASH11, DIVO11, FIND11, SPXI11
- Preço e variação diária

### 🌍 Índices Globais
- Ibovespa, S&P 500, Nasdaq, Dólar/Real, Euro/Real, Ouro, Petróleo
- Barra no topo com atualização animada

### 📰 Notícias
- 7 categorias: Brasil, EUA, China, Europa, Guerras, Cripto, Mercado
- Somente notícias das últimas 24-48h
- Ticker rolante na parte inferior com as mais relevantes

### 🤖 Análise de IA
- Resumo do mercado gerado automaticamente
- Mercado aberto: resumo curto e direto
- Mercado fechado: análise completa do dia por setor
- Recomendações específicas para Ações, Criptos e ETFs

### ⚙️ Infraestrutura
- Atualização automática em background sem travar a interface
- Frequências diferenciadas por tipo de dado
- Fallback automático: nunca mostra zero na tela
- Frontend atualiza via AJAX a cada 60 segundos, sem precisar de F5

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.10+, Flask |
| Scraping | BeautifulSoup4, Requests |
| Scheduler | APScheduler |
| Dados de cripto | CoinGecko API |
| Notícias | Google News RSS |
| IA | Groq API (llama-3.3-70b-versatile) |
| Frontend | HTML5, CSS3, JavaScript  |

---

## 🗺️ Roadmap

- Gráficos mini de variação intraday
- Alertas de preço via notificação desktop
- Modo hospedado online
- Pacote .exe para Windows
- Mais FIIs e setores customizáveis
- Dados de dividendos em tempo real

---

## 👨‍💻 Autor

**Guilherme Lima**  

---

## 📄 Licença

© 2026 Guilherme Lima · MarketPulse · Todos os direitos reservados.  
Este projeto é de uso pessoal e portfólio. Não é recomendação de investimento.

---

> ⚠️ As análises geradas por IA têm fins exclusivamente informativos e educacionais. Nenhum conteúdo constitui recomendação formal de compra ou venda de ativos. A decisão de investimento é de total responsabilidade do investidor.
