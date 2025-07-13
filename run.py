from comphone import create_app, db
from comphone.models import User, Customer, Product, Sale

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Customer': Customer,
        'Product': Product,
        'Sale': Sale
    }

if __name__ == '__main__':
    app.run(debug=True)