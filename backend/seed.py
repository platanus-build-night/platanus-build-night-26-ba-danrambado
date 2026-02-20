"""Seed script: creates 20 profiles with connections, feedback, and demo opportunities."""

import json
import uuid

import bcrypt

from app.adapters.embeddings.chroma_adapter import ChromaEmbeddingAdapter
from app.adapters.persistence.database import Base, SessionLocal, engine
from app.adapters.persistence.models import (
    ConnectionModel,
    FeedbackModel,
    MatchModel,
    OpportunityModel,
    UserModel,
)

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
        "open_to": ["job", "project", "help", "fun"],
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
        "open_to": ["job", "project", "collab", "fun"],
    },
    {
        "id": "u-paula",
        "name": "Paula Méndez",
        "email": "paula@demo.com",
        "bio": "Community organizer and event producer. Runs tech meetups and hackathons. Believes in the power of bringing the right people together.",
        "skills": ["event management", "community building", "public relations", "partnerships", "social media"],
        "interests": ["networking", "tech community", "dance", "podcasts"],
        "open_to": ["collab", "help", "project", "date", "fun"],
    },
    {
        "id": "u-nicolas",
        "name": "Nicolás Aguirre",
        "email": "nicolas@demo.com",
        "bio": "DevOps engineer and cloud architect. Automates everything. Also runs a small side project teaching kids to code.",
        "skills": ["AWS", "Terraform", "Docker", "Kubernetes", "Linux", "Python"],
        "interests": ["education", "open source", "automation", "board games"],
        "open_to": ["project", "help", "collab", "fun"],
    },
    # --- 8 new users ---
    {
        "id": "u-renata",
        "name": "Renata Silva",
        "email": "renata@demo.com",
        "bio": "Film critic and screenwriter. Runs a popular movie review blog and hosts weekly watch parties. Obsessed with sci-fi and indie cinema.",
        "skills": ["screenwriting", "film criticism", "storytelling", "content creation", "video editing"],
        "interests": ["cinema", "sci-fi", "indie films", "TV series", "creative writing"],
        "open_to": ["fun", "collab", "date"],
    },
    {
        "id": "u-tomas",
        "name": "Tomás Vargas",
        "email": "tomas@demo.com",
        "bio": "Professional chef and food blogger. Organizes pop-up dinners and cooking workshops. Believes food brings people together.",
        "skills": ["culinary arts", "food photography", "recipe development", "event hosting", "social media"],
        "interests": ["gastronomy", "travel", "wine", "cultural exchange", "sustainability"],
        "open_to": ["fun", "collab", "project", "date"],
    },
    {
        "id": "u-elena",
        "name": "Elena Quiroga",
        "email": "elena@demo.com",
        "bio": "Improv comedian and theater director. Uses improv techniques for team building workshops at tech companies. Always up for spontaneous fun.",
        "skills": ["improvisation", "public speaking", "facilitation", "creative direction", "team building"],
        "interests": ["comedy", "theater", "stand-up", "board games", "karaoke"],
        "open_to": ["fun", "collab", "help", "date"],
    },
    {
        "id": "u-gabriel",
        "name": "Gabriel Mendoza",
        "email": "gabriel@demo.com",
        "bio": "Musician and audio engineer. Produces electronic music and scores for short films. Looking for creative collaborators.",
        "skills": ["music production", "audio engineering", "Ableton Live", "sound design", "mixing"],
        "interests": ["electronic music", "film scoring", "vinyl", "photography", "festivals"],
        "open_to": ["collab", "project", "fun", "date"],
    },
    {
        "id": "u-carolina",
        "name": "Carolina Peña",
        "email": "carolina@demo.com",
        "bio": "Book club organizer and literary translator. Runs three reading groups across different genres. Passionate about connecting readers.",
        "skills": ["translation", "editing", "community management", "content curation", "writing"],
        "interests": ["literature", "languages", "philosophy", "poetry", "cultural events"],
        "open_to": ["fun", "collab", "date"],
    },
    {
        "id": "u-felipe",
        "name": "Felipe Ortiz",
        "email": "felipe@demo.com",
        "bio": "Fitness coach and outdoor adventure guide. Organizes hiking groups, trail runs, and outdoor bootcamps. Energy is contagious.",
        "skills": ["fitness training", "outdoor guiding", "nutrition", "event organization", "first aid"],
        "interests": ["hiking", "trail running", "climbing", "camping", "wellness"],
        "open_to": ["fun", "help", "date"],
    },
    {
        "id": "u-daniela",
        "name": "Daniela Ruiz",
        "email": "daniela@demo.com",
        "bio": "Language exchange coordinator and polyglot (Spanish, English, Portuguese, French). Organizes conversation tables and cultural meetups.",
        "skills": ["language teaching", "event coordination", "cross-cultural communication", "translation", "curriculum design"],
        "interests": ["languages", "travel", "cultural exchange", "cooking", "salsa dancing"],
        "open_to": ["fun", "collab", "help", "date"],
    },
    {
        "id": "u-jorge",
        "name": "Jorge Castillo",
        "email": "jorge@demo.com",
        "bio": "Tabletop gamer and game designer. Runs weekly board game nights and is designing his own strategy game. Lover of all things nerdy.",
        "skills": ["game design", "3D printing", "illustration", "community hosting", "storytelling"],
        "interests": ["board games", "D&D", "strategy games", "sci-fi", "fantasy"],
        "open_to": ["fun", "collab", "project"],
    },
]

CONNECTIONS = [
    # Original connections
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
    # New connections linking new users into the network
    ("u-renata", "u-lucas", "seed", 0.8),
    ("u-renata", "u-gabriel", "seed", 0.9),
    ("u-tomas", "u-paula", "seed", 0.7),
    ("u-tomas", "u-daniela", "seed", 0.8),
    ("u-elena", "u-paula", "seed", 0.9),
    ("u-elena", "u-mateo", "seed", 0.6),
    ("u-gabriel", "u-andres", "seed", 0.5),
    ("u-carolina", "u-camila", "seed", 0.7),
    ("u-carolina", "u-renata", "seed", 0.8),
    ("u-felipe", "u-mariana", "seed", 0.7),
    ("u-felipe", "u-diego", "seed", 0.6),
    ("u-daniela", "u-valentina", "seed", 0.7),
    ("u-jorge", "u-nicolas", "seed", 0.8),
    ("u-jorge", "u-sebastian", "seed", 0.7),
    ("u-jorge", "u-lucas", "seed", 0.9),
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
    ("u-paula", "u-elena", "fun", "Elena is hilarious. Her improv games made our team retreat the most memorable event of the year."),
    ("u-mateo", "u-elena", "collab", "Great facilitator. She used improv techniques in our brainstorming session and the ideas were 10x better than usual."),
]

# Pre-seeded demo opportunities with hand-written match explanations
DEMO_OPPORTUNITIES = [
    {
        "id": "opp-date-1",
        "title": "Coffee and conversation about sustainability",
        "description": "Looking for someone who cares about the planet as much as I do. I'd love to have a long coffee chat about sustainability, circular economy, or social impact. Open to meeting new people who share these values.",
        "type": "date",
        "posted_by": "u-sofia",
        "matches": [
            {"user_id": "u-mariana", "score": 0.92, "emb": 0.82, "net": 0.10, "rank": 1, "explanation": "Mariana shares your passion for climate action and circular economy. As a sustainability consultant, she brings deep expertise on the topics you care about most. You're already connected, so this would be a natural next step."},
            {"user_id": "u-mateo", "score": 0.85, "emb": 0.70, "net": 0.15, "rank": 2, "explanation": "Mateo's background in social entrepreneurship aligns with your interest in social impact. He's a natural connector who loves deep conversations. Direct connection in your network."},
            {"user_id": "u-camila", "score": 0.78, "emb": 0.70, "net": 0.08, "rank": 3, "explanation": "Camila cares about AI ethics and education -- topics adjacent to sustainability. She's connected to you through Diego and is described by others as genuine and warm."},
        ],
    },
    {
        "id": "opp-project-1",
        "title": "Looking for a data scientist to build an NLP-powered recommendation engine",
        "description": "Building a recommendation engine for a green marketplace. Need someone strong in NLP, Python, and ML to design the matching algorithm. 3-month part-time project, equity possible.",
        "type": "project",
        "posted_by": "u-diego",
        "matches": [
            {"user_id": "u-camila", "score": 0.95, "emb": 0.85, "net": 0.10, "rank": 1, "explanation": "Camila specializes in NLP and recommendation systems -- exactly what you need. She has TensorFlow and data analysis skills, and she's a direct connection. Her community impression highlights her rigorous, high-quality work."},
            {"user_id": "u-sebastian", "score": 0.88, "emb": 0.80, "net": 0.08, "rank": 2, "explanation": "Sebastián's deep learning and Python expertise make him a strong technical fit. He's published research in AI and is eager to apply his work to real products. Connected through Camila."},
            {"user_id": "u-lucas", "score": 0.75, "emb": 0.75, "net": 0.00, "rank": 3, "explanation": "Lucas brings strong Python and backend skills. While his focus is fintech, his systems architecture experience would be valuable for building scalable recommendation infrastructure."},
        ],
    },
    {
        "id": "opp-fun-1",
        "title": "Weekend sci-fi movie marathon and discussion group",
        "description": "Organizing a weekend sci-fi movie marathon! Plan is to watch Blade Runner, Arrival, and Ex Machina, then discuss the themes over pizza. Looking for fellow sci-fi nerds who love analyzing films.",
        "type": "fun",
        "posted_by": "u-renata",
        "matches": [
            {"user_id": "u-lucas", "score": 0.90, "emb": 0.80, "net": 0.10, "rank": 1, "explanation": "Lucas lists sci-fi as a core interest and is open to fun activities. He's a direct connection and his analytical mind would bring great depth to film discussions."},
            {"user_id": "u-jorge", "score": 0.85, "emb": 0.78, "net": 0.07, "rank": 2, "explanation": "Jorge is a self-described lover of all things nerdy, with interests in sci-fi and fantasy. He's connected through Lucas and would bring creative storytelling perspectives to the discussion."},
            {"user_id": "u-sebastian", "score": 0.78, "emb": 0.73, "net": 0.05, "rank": 3, "explanation": "Sebastián's interests include astronomy and AI -- themes central to the films you've picked. He's open to fun and connected through the network via multiple paths."},
        ],
    },
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

    print(f"Seeding {len(DEMO_OPPORTUNITIES)} demo opportunities with matches...")
    for opp in DEMO_OPPORTUNITIES:
        opp_model = OpportunityModel(
            id=opp["id"],
            title=opp["title"],
            description=opp["description"],
            type=opp["type"],
            posted_by=opp["posted_by"],
        )
        session.add(opp_model)
        session.commit()

        for m in opp["matches"]:
            match_model = MatchModel(
                id=str(uuid.uuid4()),
                opportunity_id=opp["id"],
                user_id=m["user_id"],
                score=m["score"],
                embedding_score=m["emb"],
                network_score=m["net"],
                explanation=m["explanation"],
                rank=m["rank"],
            )
            session.add(match_model)
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
