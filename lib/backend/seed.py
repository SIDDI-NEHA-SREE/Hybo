import logging
from .db import SessionLocal, engine, Base
from .models import User, Announcement, Complaint
from .auth import get_password_hash
from .rag import rag_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    logger.info("Starting database seeding...")
    db = SessionLocal()
    
    # 1. Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed Default Users
    users_to_seed = [
        {
            "email": "admin@hybo.gov",
            "mobile": "9999999999",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "official@hybo.gov",
            "mobile": "8888888888",
            "password": "official123",
            "role": "official"
        },
        {
            "email": "resident@hybo.gov",
            "mobile": "7777777777",
            "password": "resident123",
            "role": "resident"
        }
    ]
    
    for u_info in users_to_seed:
        # Check if user exists by email
        user = db.query(User).filter(User.email == u_info["email"]).first()
        if not user:
            hashed_password = get_password_hash(u_info["password"])
            user = User(
                email=u_info["email"],
                mobile=u_info["mobile"],
                password_hash=hashed_password,
                role=u_info["role"]
            )
            db.add(user)
            logger.info(f"Seeded user: {u_info['email']} with role {u_info['role']}")
        else:
            logger.info(f"User {u_info['email']} already exists.")
            
    db.commit()

    # 3. Seed Default RAG Knowledge base (Hyderabad Specifics)
    logger.info("Seeding FAISS knowledge base...")
    rag_manager.clear_index()  # Clear existing index to avoid duplicates

    knowledge_articles = [
        # Emergency
        {
            "title": "Emergency Helplines and Contacts",
            "category": "Emergency Numbers",
            "source": "official_emergency_directory.txt",
            "text": (
                "Hyderabad City Emergency Numbers:\n"
                "- Police Control Room: 100\n"
                "- Fire Control Room: 101\n"
                "- Ambulance Services: 108\n"
                "- Disaster Management (GHMC): 040-21111111\n"
                "- Women Helpline: 181 or She Teams at 9490616555\n"
                "- Child Helpline: 1098\n"
                "- Hyderabad Metro Water Supply (HMWSSB): 155313\n"
                "- Electricity Complaints (TSSPDCL): 1912\n"
                "- Traffic Control Room Helpline: 040-27852482"
            )
        },
        # Schemes
        {
            "title": "Telangana State Aarogyasri Health Scheme",
            "category": "Government Schemes",
            "source": "aarogyasri_guidelines.txt",
            "text": (
                "The Aarogyasri Health Scheme is a flagship health insurance initiative by the Telangana government. "
                "It provides quality medical care to families living below the poverty line (BPL). "
                "The scheme covers surgeries and therapies up to Rs. 5 Lakhs per family per year. "
                "Beneficiaries can access free treatment in pre-registered corporate and government network hospitals. "
                "To apply, residents need a Food Security Card (Ration Card) and must register on the Aarogyasri portal."
            )
        },
        {
            "title": "Telangana Gruha Jyothi Free Electricity Scheme",
            "category": "Government Schemes",
            "source": "gruha_jyothi_announcement.txt",
            "text": (
                "The Gruha Jyothi scheme provides up to 200 units of free domestic electricity to eligible households in Telangana. "
                "To avail of the scheme, citizens must submit a physical or online application through the Praja Palana program. "
                "The application requires linkings with Aadhaar card, customer account number (USC) of TSSPDCL, and native address proof. "
                "Housholds consuming less than 200 units monthly receive zero-electricity bills."
            )
        },
        # Transport
        {
            "title": "Hyderabad Metro Rail Network and Routes",
            "category": "Hyderabad Metro",
            "source": "metro_guide.txt",
            "text": (
                "Hyderabad Metro Rail (HMR) operates three corridors:\n"
                "1. Red Line: Miyapur to LB Nagar (29 stations, covers key areas like Ameerpet, Nampally, MGBS, Dilsukhnagar).\n"
                "2. Blue Line: Nagole to Raidurg (23 stations, covers Secunderabad, Ameerpet, Hitec City, Mindspace).\n"
                "3. Green Line: JBS Parade Ground to MGBS (9 stations, passes through Musheerabad and RTC X Roads).\n"
                "Ameerpet is the primary interchange station for the Red and Blue lines, whereas MGBS connects Red and Green lines. "
                "Metros run from 6:00 AM to 11:00 PM daily. Smart cards and mobile ticketing apps (T-Savari) offer fare discounts."
            )
        },
        {
            "title": "MMTS Suburban Rail Services",
            "category": "MMTS",
            "source": "mmts_schedule.txt",
            "text": (
                "Multi-Modal Transport System (MMTS) is the suburban rail network connecting Hyderabad and Secunderabad. "
                "Key routes include Falaknuma to Lingampally, Hyderabad (Nampally) to Lingampally, and Secunderabad to Bolarum/Medchal. "
                "MMTS tickets are highly affordable and can be purchased at stations or via the UTS mobile app. "
                "MMTS is highly popular for daily commuters traveling to Hitec City, Hafeezpet, and Lingampally IT hubs."
            )
        },
        # Tourism
        {
            "title": "Charminar and Historic Laad Bazar",
            "category": "Tourism",
            "source": "charminar_heritage.txt",
            "text": (
                "Charminar, built in 1591 by Sultan Muhammad Quli Qutb Shah, is the global icon of Hyderabad. "
                "It is a square structure with four grand arches and four 56-meter high minarets overlooking the historic city center. "
                "Charminar stands as a monument commemorating the end of a deadly plague. "
                "Right next to Charminar is Laad Bazar, famous for traditional lacquer bangles, pearls, and Hyderabadi culinary delights."
            )
        },
        {
            "title": "Golconda Fort and Sound & Light Show",
            "category": "Tourism",
            "source": "golconda_guide.txt",
            "text": (
                "Golconda Fort is a massive medieval fortress located on the western edge of Hyderabad. "
                "Built by the Kakatiya dynasty and later fortified by Qutb Shahi kings, it is famous for its acoustic marvels, "
                "where a clap at the Fateh Darwaza entrance can be heard clear at the Bala Hissar pavilion (the highest point). "
                "The fort was once the trade center for world-famous diamonds, including the Koh-i-Noor. "
                "A popular Sound & Light show detailing the history of the fort is held every evening in English, Hindi, and Telugu."
            )
        },
        # Administration & Citizen Services
        {
            "title": "GHMC Citizen Grievance Redressal",
            "category": "Citizen Complaints",
            "source": "ghmc_grievance.txt",
            "text": (
                "The Greater Hyderabad Municipal Corporation (GHMC) offers a citizen grievance redressal system. "
                "Citizens can file complaints online via the GHMC Mobile App, the official website, or by dialing the helpline at 21111111. "
                "Categories of grievances include road repairs, streetlights, garbage collection, stray dog menace, sanitation, and water logging. "
                "Complaints are assigned a unique grievance number, forwarded to the concerned ward official, and tracked online until resolution."
            )
        },
        # History & Culture
        {
            "title": "Telangana Culture and Bonalu Festival",
            "category": "Telangana Culture",
            "source": "bonalu_history.txt",
            "text": (
                "Bonalu is a traditional Hindu festival celebrated annually in Hyderabad and Secunderabad, dedicated to Goddess Mahakali. "
                "The festival is celebrated during the Ashada Masam (July/August). Women carry decorative brass or earthen pots (Bonam) "
                "filled with cooked rice, milk, and jaggery as an offering to the Goddess. Bonalu involves traditional dance forms, "
                "Pothuraju dancers leading the procession with whips, and community feasts."
            )
        }
    ]

    for article in knowledge_articles:
        rag_manager.add_documents(
            text=article["text"],
            source=article["source"],
            title=article["title"],
            category=article["category"]
        )
        logger.info(f"Indexed article: {article['title']}")

    logger.info("Database and FAISS seeding completed successfully!")
    db.close()

if __name__ == "__main__":
    seed_database()
