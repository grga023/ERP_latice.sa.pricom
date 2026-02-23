from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(200), nullable=False)
    cena = db.Column(db.Float, nullable=False, default=0)
    placeno = db.Column(db.Boolean, default=False)
    kupac = db.Column(db.String(200), nullable=False)
    datum = db.Column(db.String(20), default='')
    kolicina = db.Column(db.Integer, default=1)
    boja = db.Column(db.String(100), default='')
    opis = db.Column(db.Text, default='')
    slika = db.Column(db.String(300), default='')
    status = db.Column(db.String(20), nullable=False, default='new')
    lager_id = db.Column(db.Integer, db.ForeignKey('lager.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'naziv': self.naziv,
            'cena': self.cena,
            'placeno': self.placeno,
            'kupac': self.kupac,
            'datum': self.datum,
            'kolicina': self.kolicina,
            'boja': self.boja,
            'opis': self.opis,
            'slika': self.slika,
            'status': self.status,
            'lager_id': self.lager_id
        }


class LagerItem(db.Model):
    __tablename__ = 'lager'

    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(200), nullable=False)
    cena = db.Column(db.Float, default=0)
    boja = db.Column(db.String(100), default='')
    kolicina = db.Column(db.Integer, default=0)
    lokacija = db.Column(db.String(100), default='Kuća')
    slika = db.Column(db.String(300), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'naziv': self.naziv,
            'cena': self.cena,
            'boja': self.boja,
            'kolicina': self.kolicina,
            'lokacija': self.lokacija,
            'slika': self.slika
        }


class EmailConfig(db.Model):
    __tablename__ = 'email_config'

    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=False)
    sender_email = db.Column(db.String(200), default='')
    app_password = db.Column(db.String(200), default='')
    receiver_email = db.Column(db.String(500), default='')
    days_before = db.Column(db.Integer, default=2)


class NotificationLog(db.Model):
    __tablename__ = 'notification_log'

    id = db.Column(db.Integer, primary_key=True)
    notify_key = db.Column(db.String(200), unique=True, nullable=False)
