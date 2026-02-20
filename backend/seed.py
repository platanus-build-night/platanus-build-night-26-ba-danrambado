"""Seed script: creates 12 diverse profiles with pre-existing connections."""

import json
import uuid

from app.adapters.embeddings.chroma_adapter import ChromaEmbeddingAdapter
from app.adapters.persistence.database import Base, SessionLocal, engine
from app.adapters.persistence.models import ConnectionModel, UserModel

USERS = [
    {
        "id": "u-sofia",
        "name": "Sofía Herrera",
        "bio": "UX designer passionate about sustainability and social impact. 5 years designing digital products for NGOs and green startups.",
        "skills": ["UX design", "user research", "Figma", "design systems", "accessibility"],
        "interests": ["sustainability", "social impact", "circular economy", "community building"],
        "open_to": ["project", "collab", "job", "date"],
    },
    {
        "id": "u-diego",
        "name": "Diego Morales",
        "bio": "Fullstack developer focused on climate tech. Built carbon tracking tools and renewable energy dashboards. TypeScript and Python enthusiast.",
        "skills": ["TypeScript", "Python", "React", "Node.js", "PostgreSQL", "AWS"],
        "interests": ["climate tech", "renewable energy", "open source", "hiking"],
        "open_to": ["project", "collab", "job", "help"],
    },
    {
        "id": "u-camila",
        "name": "Camila Vega",
        "bio": "Data scientist specializing in NLP and recommendation systems. Ex-Google, now freelancing and looking for meaningful projects.",
        "skills": ["Python", "machine learning", "NLP", "TensorFlow", "data analysis", "SQL"],
        "interests": ["AI ethics", "education", "music", "running"],
        "open_to": ["project", "collab", "help", "date"],
    },
    {
        "id": "u-mateo",
        "name": "Mateo Ríos",
        "bio": "Product manager with a background in social entrepreneurship. Launched 3 impact-driven products. Loves connecting people and ideas.",
        "skills": ["product management", "strategy", "user stories", "agile", "fundraising"],
        "interests": ["social impact", "startups", "mentoring", "photography"],
        "open_to": ["collab", "help", "project", "date"],
    },
    {
        "id": "u-valentina",
        "name": "Valentina Cruz",
        "bio": "Growth marketer who helped 10+ startups go from 0 to 10k users. Expert in content, SEO, and community-led growth.",
        "skills": [
            "growth marketing",
            "SEO",
            "content strategy",
            "analytics",
            "community building",
        ],
        "interests": ["startups", "branding", "yoga", "travel"],
        "open_to": ["job", "project", "collab", "date"],
    },
    {
        "id": "u-lucas",
        "name": "Lucas Fernández",
        "bio": "Backend engineer in fintech. Built payment systems processing millions of transactions. Interested in decentralized finance.",
        "skills": ["Go", "Python", "Kubernetes", "microservices", "PostgreSQL", "Redis"],
        "interests": ["fintech", "DeFi", "chess", "sci-fi"],
        "open_to": ["job", "project", "help"],
    },
    {
        "id": "u-isabella",
        "name": "Isabella Rojas",
        "bio": "Graphic designer and illustrator. Creates brand identities for conscious businesses. Also teaches design workshops.",
        "skills": [
            "graphic design",
            "illustration",
            "branding",
            "Adobe Creative Suite",
            "typography",
        ],
        "interests": ["art", "sustainability", "teaching", "ceramics"],
        "open_to": ["project", "collab", "help", "date"],
    },
    {
        "id": "u-andres",
        "name": "Andrés Paredes",
        "bio": "Mobile developer (iOS & Android). Built health and wellness apps with 500k+ downloads. Passionate about accessible technology.",
        "skills": ["Swift", "Kotlin", "Flutter", "Firebase", "CI/CD", "UI design"],
        "interests": ["health tech", "accessibility", "cooking", "basketball"],
        "open_to": ["job", "project", "collab"],
    },
    {
        "id": "u-mariana",
        "name": "Mariana López",
        "bio": "Environmental engineer turned sustainability consultant. Helps companies measure and reduce their carbon footprint.",
        "skills": [
            "environmental analysis",
            "carbon accounting",
            "project management",
            "data visualization",
            "public speaking",
        ],
        "interests": ["climate action", "circular economy", "surfing", "documentaries"],
        "open_to": ["collab", "project", "help", "date"],
    },
    {
        "id": "u-sebastian",
        "name": "Sebastián Torres",
        "bio": "AI researcher focused on computer vision. Published papers on object detection. Looking to apply research to real-world products.",
        "skills": ["Python", "PyTorch", "computer vision", "deep learning", "research", "C++"],
        "interests": ["AI", "robotics", "astronomy", "cycling"],
        "open_to": ["job", "project", "collab"],
    },
    {
        "id": "u-paula",
        "name": "Paula Méndez",
        "bio": "Community organizer and event producer. Runs tech meetups and hackathons. Believes in the power of bringing the right people together.",
        "skills": [
            "event management",
            "community building",
            "public relations",
            "partnerships",
            "social media",
        ],
        "interests": ["networking", "tech community", "dance", "podcasts"],
        "open_to": ["collab", "help", "project", "date"],
    },
    {
        "id": "u-nicolas",
        "name": "Nicolás Aguirre",
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
