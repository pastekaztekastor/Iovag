from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

user = User.query.filter_by(username='test').first()
if user:
    user.onboarding_completed = False
    db.session.commit()
    print(f"Utilisateur test configuré pour voir l'onboarding: onboarding_completed={user.onboarding_completed}")
else:
    print("Utilisateur test non trouvé")
