"""
MarketPulse · app.py v6
Scheduler inteligente + endpoints limpos
"""
import datetime, threading, webbrowser
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from data import coletar_tudo, get_dados, get_status, is_pronto

app = Flask(__name__)

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/painel")
def painel():
    return render_template("painel.html")

@app.route("/api/dados")
def api_dados():
    if not is_pronto():
        return jsonify({"ok":False,"carregando":True,
                        "msg":"Coletando dados pela primeira vez... aguarde ~30s"}), 202
    return jsonify({"ok":True,"dados":get_dados()})

@app.route("/api/status")
def api_status():
    return jsonify({"pronto":is_pronto(),"api":get_status()})

def _iniciar_scheduler():
    sched = BackgroundScheduler(daemon=True, timezone="America/Sao_Paulo",
                                 job_defaults={"max_instances":1,"coalesce":True})
    sched.add_job(coletar_tudo, "interval", seconds=30,
                  id="coleta", next_run_time=datetime.datetime.now())
    sched.start()
    return sched

def _abrir_browser():
    import time; time.sleep(2)
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    print("=" * 55)
    print("  MarketPulse v6")
    print("  Landing : http://localhost:5000")
    print("  Painel  : http://localhost:5000/painel")
    print("  Dados coletados automaticamente a cada 30s")
    print("  (Brapi + Google Finance + CoinGecko + Groq IA)")
    print("=" * 55)

    sched = _iniciar_scheduler()
    threading.Thread(target=_abrir_browser, daemon=True).start()
    try:
        app.run(debug=False, port=5000, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        sched.shutdown(wait=False)
