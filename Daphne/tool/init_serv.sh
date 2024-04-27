echo "Start daphne server"
daphne -b 0.0.0.0 -p 8002 TranServer.asgi:application
