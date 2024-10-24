import connexion

app = connexion.App("kutya", specification_dir='./Rel17-bundle')
#app.add_api('swagger.yaml')
app.add_api('test2.yaml')
app.run(port=8080)
