import connexion

app = connexion.App(__name__, specification_dir='./')
app.add_api('swagger_withsec.yaml')
app.run(port=8080)
