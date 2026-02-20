"""Seed script: creates 12 diverse profiles with connections and feedback."""

import json
import uuid

import bcrypt

from app.adapters.embeddings.chroma_adapter import ChromaEmbeddingAdapter
from app.adapters.persistence.database import Base, SessionLocal, engine
from app.adapters.persistence.models import ConnectionModel, FeedbackModel, UserModel

DEMO_PASSWORD_HASH = bcrypt.hashpw(b"demo123", bcrypt.gensalt()).decode()

USERS = [
    {
        "id": "u-sofia",
        "name": "Sofía Herrera",
        "email": "sofia@demo.com",
        "bio": "UX designer passionate about sustainability and social impact. 5 years designing digital products for NGOs and green startups.",
        "skills": ["UX design", "user research", "Figma", "design systems", "accessibility"],
        "interests": ["sustainability", "social impact", "circular economy", "community building"],
        "open_to": ["project", "collab", "job", "date"],
    },
    {
        "id": "u-diego",
        "name": "Diego Morales",
        "email": "diego@demo.com",
        "bio": "Fullstack developer focused on climate tech. Built carbon tracking tools and renewable energy dashboards. TypeScript and Python enthusiast.",
        "skills": ["TypeScript", "Python", "React", "Node.js", "PostgreSQL", "AWS"],
        "interests": ["climate tech", "renewable energy", "open source", "hiking"],
        "open_to": ["project", "collab", "job", "help"],
    },
    {
        "id": "u-camila",
        "name": "Camila Vega",
        "email": "camila@demo.com",
        "bio": "Data scientist specializing in NLP and recommendation systems. Ex-Google, now freelancing and looking for meaningful projects.",
        "skills": ["Python", "machine learning", "NLP", "TensorFlow", "data analysis", "SQL"],
        "interests": ["AI ethics", "education", "music", "running"],
        "open_to": ["project", "collab", "help", "date"],
    },
    {
        "id": "u-mateo",
        "name": "Mateo Ríos",
        "email": "mateo@demo.com",
        "bio": "Product manager with a background in social entrepreneurship. Launched 3 impact-driven products. Loves connecting people and ideas.",
        "skills": ["product management", "strategy", "user stories", "agile", "fundraising"],
        "interests": ["social impact", "startups", "mentoring", "photography"],
        "open_to": ["collab", "help", "project", "date"],
    },
    {
        "id": "u-valentina",
        "name": "Valentina Cruz",
        "email": "valentina@demo.com",
        "bio": "Growth marketer who helped 10+ startups go from 0 to 10k users. Expert in content, SEO, and community-led growth.",
        "skills": ["growth marketing", "SEO", "content strategy", "analytics", "community building"],
        "interests": ["startups", "branding", "yoga", "travel"],
        "open_to": ["job", "project", "collab", "date"],
    },
    {
        "id": "u-lucas",
        "name": "Lucas Fernández",
        "email": "lucas@demo.com",
        "bio": "Backend engineer in fintech. Built payment systems processing millions of transactions. Interested in decentralized finance.",
        "skills": ["Go", "Python", "Kubernetes", "microservices", "PostgreSQL", "Redis"],
        "interests": ["fintech", "DeFi", "chess", "sci-fi"],
        "open_to": ["job", "project", "help"],
    },
    {
        "id": "u-isabella",
        "name": "Isabella Rojas",
        "email": "isabella@demo.com",
        "bio": "Graphic designer and illustrator. Creates brand identities for conscious businesses. Also teaches design workshops.",
        "skills": ["graphic design", "illustration", "branding", "Adobe Creative Suite", "typography"],
        "interests": ["art", "sustainability", "teaching", "ceramics"],
        "open_to": ["project", "collab", "help", "date"],
    },
    {
        "id": "u-andres",
        "name": "Andrés Paredes",
        "email": "andres@demo.com",
        "bio": "Mobile developer (iOS & Android). Built health and wellness apps with 500k+ downloads. Passionate about accessible technology.",
        "skills": ["Swift", "Kotlin", "Flutter", "Firebase", "CI/CD", "UI design"],
        "interests": ["health tech", "accessibility", "cooking", "basketball"],
        "open_to": ["job", "project", "collab"],
    },
    {
        "id": "u-mariana",
        "name": "Mariana López",
        "email": "mariana@demo.com",
        "bio": "Environmental engineer turned sustainability consultant. Helps companies measure and reduce their carbon footprint.",
        "skills": ["environmental analysis", "carbon accounting", "project management", "data visualization", "public speaking"],
        "interests": ["climate action", "circular economy", "surfing", "documentaries"],
        "open_to": ["collab", "project", "help", "date"],
    },
    {
        "id": "u-sebastian",
        "name": "Sebastián Torres",
        "email": "sebastian@demo.com",
        "bio": "AI researcher focused on computer vision. Published papers on object detection. Looking to apply research to real-world products.",
        "skills": ["Python", "PyTorch", "computer vision", "deep learning", "research", "C++"],
        "interests": ["AI", "robotics", "astronomy", "cycling"],
        "open_to": ["job", "project", "collab"],
    },
    {
        "id": "u-paula",
        "name": "Paula Méndez",
        "email": "paula@demo.com",
        "bio": "Community organizer and event producer. Runs tech meetups and hackathons. Believes in the power of bringing the right people together.",
        "skills": ["event management", "community building", "public relations", "partnerships", "social media"],
        "interests": ["networking", "tech community", "dance", "podcasts"],
        "open_to": ["collab", "help", "project", "date"],
    },
    {
        "id": "u-nicolas",
        "name": "Nicolás Aguirre",
        "email": "nicolas@demo.com",
        "bio": "DevOps engineer and cloud architect. Automates everything. Also runs a small side project teaching kids to code.",
        "skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Linux", "Python"],
        "interests": ["education", "open source", "automation", "board games"],
        "open_to": ["project", "help", "collab"],
    },
]

CONNECTIONS = [
    ("u-sofia", "u-diego", "seed", 1.0),
    ("u-diego", "u-camila", "seed", 1.0),
    ("u-sofia", "u-mateo", "seed", 1.0),
    ("u-valentina", "u-mateo", "seed", 1.0),
    ("u-sofia", "u-isabella", "seed", 0.8),
    ("u-isabella", "u-mariana", "seed", 0.8),
    ("u-diego", "u-nicolas", "seed", 0.9),
    ("u-camila", "u-sebastian", "seed", 0.9),
    ("u-paula", "u-valentina", "seed", 0.8),
    ("u-paula", "u-mateo", "seed", 0.7),
    ("u-andres", "u-diego", "seed", 0.6),
    ("u-mariana", "u-sofia", "seed", 0.7),
]

FEEDBACKS = [
    ("u-diego", "u-sofia", "project", "Incredible eye for design. She understood the user needs immediately and delivered mockups that were spot-on. Very easy to collaborate with."),
    ("u-mateo", "u-sofia", "collab", "Sofía brings structure and empathy to every project. She helped us rethink our entire onboarding flow in one afternoon."),
    ("u-camila", "u-sofia", "date", "Really fun person to hang out with. We talked for hours about sustainability and tech. Genuine and warm."),
    ("u-sofia", "u-diego", "project", "Diego is a machine. He shipped a full dashboard in two days. Clear communicator, always on time with deliverables."),
    ("u-nicolas", "u-diego", "collab", "Solid engineer. He helped me debug a nasty Kubernetes issue in minutes. Very generous with his time."),
    ("u-andres", "u-diego", "project", "Great to pair-program with. Patient, explains things well, and writes very clean code."),
    ("u-sofia", "u-mateo", "collab", "Mateo is a connector. He introduced me to three people who became collaborators. Great strategic thinker."),
    ("u-valentina", "u-mateo", "date", "Fun, thoughtful, and easy to talk to. We had a great conversation about startups and social impact over coffee."),
    ("u-diego", "u-camila", "project", "Camila's NLP expertise is impressive. She built a prototype classifier in a day that outperformed our previous model."),
    ("u-sebastian", "u-camila", "collab", "Very rigorous researcher. She always backs up her ideas with data. Sometimes takes a while to respond, but always delivers quality."),
]


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    existing = session.query(UserModel).count()
    if existing > 0:
        print(f"Database already has {existing} users. Skipping seed.")
        session.close()
        return

    print(f"Seeding {len(USERS)} users...")
    for u in USERS:
        model = UserModel(
            id=u["id"],
            name=u["name"],
            email=u["email"],
            password_hash=DEMO_PASSWORD_HASH,
            bio=u["bio"],
            skills=json.dumps(u["skills"]),
            interests=json.dumps(u["interests"]),
            open_to=json.dumps(u["open_to"]),
        )
        session.add(model)
    session.commit()

    print(f"Seeding {len(CONNECTIONS)} connections...")
    for user_a, user_b, source, strength in CONNECTIONS:
        model = ConnectionModel(
            id=str(uuid.uuid4()),
            user_a=user_a,
            user_b=user_b,
            source=source,
            strength=strength,
        )
        session.add(model)
    session.commit()

    print(f"Seeding {len(FEEDBACKS)} feedback entries...")
    for from_id, to_id, opp_type, text in FEEDBACKS:
        model = FeedbackModel(
            id=str(uuid.uuid4()),
            from_user_id=from_id,
            to_user_id=to_id,
            opportunity_type=opp_type,
            text=text,
        )
        session.add(model)
    session.commit()

    print("Embedding profiles into ChromaDB...")
    chroma = ChromaEmbeddingAdapter()
    for u in USERS:
        text = (
            f"{u['bio']}. "
            f"Skills: {', '.join(u['skills'])}. "
            f"Interests: {', '.join(u['interests'])}. "
            f"Open to: {', '.join(u['open_to'])}"
        )
        chroma.upsert_profile(u["id"], text, {"name": u["name"], "open_to": ",".join(u["open_to"])})

    session.close()
    print("Seed complete!")


if __name__ == "__main__":
    seed()
