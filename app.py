from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
import requests
import json
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-key-change-me")

def init_db():

    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_folder = os.path.join(base_dir, "database")

    os.makedirs(database_folder, exist_ok=True)

    database_path = os.path.join(
        database_folder,
        "bookdiscovery.db"
    )

    connection = sqlite3.connect(database_path)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            description TEXT,
            publisher TEXT,
            pages INTEGER,
            rating REAL,
            publication_date TEXT,
            isbn TEXT,
            category TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()

# Backup books
backup_books = [
    {
    "id": 1,
    "volumeInfo": {
        "title": "Atomic Habits",
            "authors": ["James Clear"],
            "description": "A practical guide to building good habits, breaking bad ones, and making small changes that lead to meaningful results.",
            "isbn": "9780735211292",
            "publishedDate": "2018",
            "publisher": "Avery",
            "pageCount": 320,
            "rating": 4.8,
            "categories": ["Self-Help", "Personal Development"],
            "goals": ["Study & Learning", "Habits & Discipline", "Personal Growth"],
            "styles": ["Practical"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books?id=6F0HEAAAQBAJ"
        }
    },
    {
    "id": 2,    
        "volumeInfo": {
            "title": "The 7 Habits of Highly Effective People",
            "authors": ["Stephen R. Covey"],
            "description": "A personal development book that presents principles for improving effectiveness, relationships, and personal responsibility.",
            "isbn": "9781982137274",
            "publishedDate": "1989",
            "publisher": "Simon & Schuster",
            "pageCount": 464,
            "rating": 4.7,
            "categories": ["Self-Help", "Personal Development"],
            "goals": ["Habits & Discipline", "Personal Growth", "Communication", "Career & Success"],
            "styles": ["Practical", "Psychological"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
    "id": 3,
        "volumeInfo": {
            "title": "Think and Grow Rich",
            "authors": ["Napoleon Hill"],
            "description": "A classic personal development book focusing on mindset, goals, persistence, and principles for achieving success.",
            "isbn": "9781585424337",
            "publishedDate": "1937",
            "publisher": "TarcherPerigee",
            "pageCount": 320,
            "rating": 4.7,
            "categories": ["Self-Help", "Success"],
            "goals": ["Personal Growth", "Career & Success", "Finance"],
            "styles": ["Inspirational"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
    "id": 4,    
        "volumeInfo": {
            "title": "The Power of Now",
            "authors": ["Eckhart Tolle"],
            "description": "A guide to understanding the importance of living in the present moment and developing greater awareness.",
            "isbn": "9781577314806",
            "publishedDate": "1997",
            "publisher": "New World Library",
            "pageCount": 236,
            "rating": 4.7,
            "categories": ["Self-Help", "Spirituality"],
            "goals": ["Personal Growth", "Mindfulness"],
            "styles": ["Psychological"],
            "experiences": ["Beginner", "Quick"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
    "id": 5,
        "volumeInfo": {
            "title": "How to Win Friends and Influence People",
            "authors": ["Dale Carnegie"],
            "description": "A classic guide about communication, relationships, understanding people, and developing better social skills.",
            "isbn": "9780671027032",
            "publishedDate": "1936",
            "publisher": "Simon & Schuster",
            "pageCount": 288,
            "rating": 4.7,
            "categories": ["Self-Help", "Communication"],
            "goals": ["Communication", "Personal Growth", "Career & Success"],
            "styles": ["Practical", "Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
    "id": 6,
        "volumeInfo": {
            "title": "The Psychology of Money",
            "authors": ["Morgan Housel"],
            "description": "A collection of lessons about how people think about money, saving, investing, risk, and financial decisions.",
            "isbn": "9780857197689",
            "publishedDate": "2020",
            "publisher": "Harriman House",
            "pageCount": 256,
            "rating": 4.7,
            "categories": ["Finance", "Personal Development"],
            "goals": ["Finance", "Personal Growth", "Career & Success"],
            "styles": ["Practical", "Psychological"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 7,
        "volumeInfo": {
            "title": "The Power of Habit",
            "authors": ["Charles Duhigg"],
            "description": "An exploration of how habits work and how understanding habit loops can help people change their routines.",
            "isbn": "9780812981605",
            "publishedDate": "2012",
            "publisher": "Random House",
            "pageCount": 371,
            "rating": 4.6,
            "categories": ["Psychology", "Personal Development"],
            "goals": ["Habits & Discipline", "Personal Growth"],
            "styles": ["Psychological", "Practical"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 8,
        "volumeInfo": {
            "title": "The Lean Startup",
            "authors": ["Eric Ries"],
            "description": "A practical approach to developing products, testing ideas, learning from customers, and building businesses efficiently.",
            "isbn": "9780307887894",
            "publishedDate": "2011",
            "publisher": "Crown Business",
            "pageCount": 336,
            "rating": 4.5,
            "categories": ["Business", "Entrepreneurship"],
            "goals": ["Career & Success", "Personal Growth"],
            "styles": ["Practical"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 9,
        "volumeInfo": {
            "title": "Rich Dad Poor Dad",
            "authors": ["Robert T. Kiyosaki"],
            "description": "A personal finance book that discusses financial education, money mindset, assets, liabilities, and financial independence.",
            "isbn": "9781612680194",
            "publishedDate": "1997",
            "publisher": "Plata Publishing",
            "pageCount": 336,
            "rating": 4.6,
            "categories": ["Finance", "Business"],
            "goals": ["Finance", "Career & Success", "Personal Growth"],
            "styles": ["Practical", "Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 10,
        "volumeInfo": {
            "title": "Mindset",
            "authors": ["Carol S. Dweck"],
            "description": "A psychology-based book explaining how different beliefs about ability and learning can influence personal growth and achievement.",
            "isbn": "9780345472328",
            "publishedDate": "2006",
            "publisher": "Random House",
            "pageCount": 320,
            "rating": 4.6,
            "categories": ["Psychology", "Personal Development", "Education & Learning"],
            "goals": ["Personal Growth", "Study & Learning", "Career & Success"],
            "styles": ["Psychological", "Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 11,
        "volumeInfo": {
            "title": "Deep Work",
            "authors": ["Cal Newport"],
            "description": "A guide to developing focused concentration and reducing distractions in order to perform meaningful and demanding work.",
            "isbn": "9781455586691",
            "publishedDate": "2016",
            "publisher": "Grand Central Publishing",
            "pageCount": 304,
            "rating": 4.6,
            "categories": ["Career & Success", "Productivity", "Education & Learning"],
            "goals": ["Study & Learning", "Career & Success", "Habits & Discipline"],
            "styles": ["Practical"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 12,
        "volumeInfo": {
            "title": "How to Talk to Anyone",
            "authors": ["Leil Lowndes"],
            "description": "A practical guide to improving conversations, social confidence, communication skills, and relationships.",
            "isbn": "9780071418584",
            "publishedDate": "2003",
            "publisher": "McGraw-Hill",
            "pageCount": 368,
            "rating": 4.5,
            "categories": ["Communication", "Self-Help"],
            "goals": ["Communication", "Personal Growth", "Career & Success"],
            "styles": ["Practical"],
            "experiences": ["Beginner", "Quick"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 13,
        "volumeInfo": {
            "title": "The 5 AM Club",
            "authors": ["Robin Sharma"],
            "description": "A personal development book focused on building productive routines, discipline, focus, and a strong morning routine.",
            "isbn": "9781443456623",
            "publishedDate": "2018",
            "publisher": "HarperCollins",
            "pageCount": 336,
            "rating": 4.4,
            "categories": ["Personal Growth", "Self-Help"],
            "goals": ["Habits & Discipline", "Personal Growth", "Career & Success"],
            "styles": ["Inspirational", "Practical"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 14,
        "volumeInfo": {
            "title": "The Subtle Art of Not Giving a F*ck",
            "authors": ["Mark Manson"],
            "description": "A modern personal development book about values, responsibility, challenges, and developing a healthier perspective on life.",
            "isbn": "9780062457714",
            "publishedDate": "2016",
            "publisher": "Harper",
            "pageCount": 224,
            "rating": 4.2,
            "categories": ["Self-Help", "Personal Development"],
            "goals": ["Personal Growth", "Mindfulness"],
            "styles": ["Psychological", "Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 15,
        "volumeInfo": {
            "title": "Zero to One",
            "authors": ["Peter Thiel", "Blake Masters"],
            "description": "A business and entrepreneurship book about innovation, creating new ideas, and building companies that develop something unique.",
            "isbn": "9780804139298",
            "publishedDate": "2014",
            "publisher": "Crown Business",
            "pageCount": 224,
            "rating": 4.4,
            "categories": ["Business", "Entrepreneurship"],
            "goals": ["Career & Success", "Personal Growth"],
            "styles": ["Practical"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 16,
        "volumeInfo": {
            "title": "The Intelligent Investor",
            "authors": ["Benjamin Graham"],
            "description": "A classic introduction to investment principles, financial decision-making, risk management, and long-term investing.",
            "isbn": "9780060555665",
            "publishedDate": "1949",
            "publisher": "HarperBusiness",
            "pageCount": 640,
            "rating": 4.4,
            "categories": ["Finance", "Business"],
            "goals": ["Finance", "Career & Success"],
            "styles": ["Practical", "Detailed"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 17,
        "volumeInfo": {
            "title": "Quiet",
            "authors": ["Susan Cain"],
            "description": "An exploration of introversion, personality, communication, and the strengths that different personality styles can bring to work and life.",
            "isbn": "9780307352156",
            "publishedDate": "2012",
            "publisher": "Crown",
            "pageCount": 368,
            "rating": 4.5,
            "categories": ["Psychology", "Communication"],
            "goals": ["Communication", "Personal Growth", "Career & Success"],
            "styles": ["Psychological"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 18,
        "volumeInfo": {
            "title": "The 48 Laws of Power",
            "authors": ["Robert Greene"],
            "description": "A book examining historical examples and strategies related to power, influence, social behavior, and human relationships.",
            "isbn": "9780140280197",
            "publishedDate": "1998",
            "publisher": "Penguin Books",
            "pageCount": 480,
            "rating": 4.4,
            "categories": ["Psychology", "Business"],
            "goals": ["Communication", "Career & Success", "Personal Growth"],
            "styles": ["Psychological", "Detailed"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 19,
        "volumeInfo": {
            "title": "Steve Jobs",
            "authors": ["Walter Isaacson"],
            "description": "A biography of Steve Jobs that explores his life, career, personality, and role in the development of influential technology products.",
            "isbn": "9781451648539",
            "publishedDate": "2011",
            "publisher": "Simon & Schuster",
            "pageCount": 656,
            "rating": 4.5,
            "categories": ["Biography", "Business"],
            "goals": ["Career & Success", "Personal Growth"],
            "styles": ["Inspirational", "Detailed"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 20,
        "volumeInfo": {
            "title": "The Diary of a Young Girl",
            "authors": ["Anne Frank"],
            "description": "The diary of Anne Frank provides a personal account of her life, thoughts, hopes, and experiences during a difficult period of history.",
            "isbn": "9780553296983",
            "publishedDate": "1947",
            "publisher": "Bantam",
            "pageCount": 352,
            "rating": 4.6,
            "categories": ["Biography", "History"],
            "goals": ["Personal Growth"],
            "styles": ["Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 21,
        "volumeInfo": {
            "title": "The Art of Happiness",
            "authors": ["Dalai Lama", "Howard C. Cutler"],
            "description": "A practical exploration of happiness, compassion, and mental well-being that combines Buddhist teachings with modern psychological perspectives.",
            "isbn": "9781573221115",
            "publishedDate": "1998",
            "publisher": "Riverhead Books",
            "pageCount": 336,
            "rating": 4.5,
            "categories": ["Philosophy & Mindfulness", "Self-Help"],
            "goals": ["Personal Growth", "Mindfulness"],
            "styles": ["Psychological", "Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 22,
        "volumeInfo": {
            "title": "The Book of Joy",
            "authors": ["Dalai Lama", "Desmond Tutu", "Douglas Abrams"],
            "description": "A conversation about finding joy, compassion, resilience, and meaning in everyday life.",
            "isbn": "9780399185045",
            "publishedDate": "2016",
            "publisher": "Avery",
            "pageCount": 384,
            "rating": 4.6,
            "categories": ["Philosophy & Mindfulness", "Personal Growth"],
            "goals": ["Personal Growth", "Mindfulness"],
            "styles": ["Inspirational", "Psychological"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 23,
        "volumeInfo": {
            "title": "A Brief History of Time",
            "authors": ["Stephen Hawking"],
            "description": "A fascinating introduction to major ideas about the universe, including time, space, black holes, and the origins of the cosmos.",
            "isbn": "9780553380163",
            "publishedDate": "1988",
            "publisher": "Bantam",
            "pageCount": 256,
            "rating": 4.6,
            "categories": ["Science"],
            "goals": ["Study & Learning"],
            "styles": ["Detailed"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 24,
        "volumeInfo": {
            "title": "Cosmos",
            "authors": ["Carl Sagan"],
            "description": "A journey through the universe that explores astronomy, science, evolution, and humanity's place in the cosmos.",
            "isbn": "9780345539434",
            "publishedDate": "1980",
            "publisher": "Random House",
            "pageCount": 384,
            "rating": 4.7,
            "categories": ["Science"],
            "goals": ["Study & Learning"],
            "styles": ["Inspirational", "Detailed"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 25,
        "volumeInfo": {
            "title": "The Selfish Gene",
            "authors": ["Richard Dawkins"],
            "description": "An accessible exploration of evolution, natural selection, genes, and the way evolutionary ideas can explain animal and human behaviour.",
            "isbn": "9780198788607",
            "publishedDate": "1976",
            "publisher": "Oxford University Press",
            "pageCount": 384,
            "rating": 4.5,
            "categories": ["Science"],
            "goals": ["Study & Learning"],
            "styles": ["Detailed", "Psychological"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 26,
        "volumeInfo": {
            "title": "On Writing Well",
            "authors": ["William Zinsser"],
            "description": "A practical guide to clear, simple, and effective writing for anyone who wants to communicate ideas with confidence.",
            "isbn": "9780060891541",
            "publishedDate": "1976",
            "publisher": "Harper Perennial",
            "pageCount": 336,
            "rating": 4.5,
            "categories": ["Creativity & Writing", "Education & Learning"],
            "goals": ["Study & Learning", "Personal Growth"],
            "styles": ["Practical"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 27,
        "volumeInfo": {
            "title": "Big Magic",
            "authors": ["Elizabeth Gilbert"],
            "description": "An encouraging exploration of creativity, curiosity, and the process of bringing creative ideas into everyday life.",
            "isbn": "9781594634727",
            "publishedDate": "2015",
            "publisher": "Riverhead Books",
            "pageCount": 288,
            "rating": 4.4,
            "categories": ["Creativity & Writing", "Personal Growth"],
            "goals": ["Personal Growth"],
            "styles": ["Inspirational"],
            "experiences": ["Beginner", "Quick"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 28,
        "volumeInfo": {
            "title": "Steal Like an Artist",
            "authors": ["Austin Kleon"],
            "description": "A short and practical guide to creativity that encourages people to collect ideas, experiment, and develop their own creative style.",
            "isbn": "9780761169253",
            "publishedDate": "2012",
            "publisher": "Workman Publishing",
            "pageCount": 160,
            "rating": 4.4,
            "categories": ["Creativity & Writing"],
            "goals": ["Personal Growth"],
            "styles": ["Practical", "Inspirational"],
            "experiences": ["Beginner", "Quick"],
            "infoLink": "https://books.google.com/books"
        }
    },
    {
        "id": 29,
        "volumeInfo": {
            "title": "Leonardo da Vinci",
            "authors": ["Walter Isaacson"],
            "description": "A biography of Leonardo da Vinci exploring his life, creativity, scientific curiosity, and artistic achievements.",
            "isbn": "9781501139154",
            "publishedDate": "2017",
            "publisher": "Simon & Schuster",
            "pageCount": 624,
            "rating": 4.5,
            "categories": ["Biography", "Creativity & Writing"],
            "goals": ["Personal Growth", "Study & Learning"],
            "styles": ["Inspirational", "Detailed"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 30,
        "volumeInfo": {
            "title": "Becoming",
            "authors": ["Michelle Obama"],
            "description": "A memoir about personal experiences, growth, family, work, and public life.",
            "isbn": "9781524763138",
            "publishedDate": "2018",
            "publisher": "Crown",
            "pageCount": 448,
            "rating": 4.7,
            "categories": ["Biography"],
            "goals": ["Personal Growth", "Career & Success"],
            "styles": ["Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 31,
        "volumeInfo": {
            "title": "Man's Search for Meaning",
            "authors": ["Viktor E. Frankl"],
            "description": "A reflection on meaning, resilience, and the human search for purpose.",
            "isbn": "9780807014271",
            "publishedDate": "1946",
            "publisher": "Beacon Press",
            "pageCount": 184,
            "rating": 4.7,
            "categories": ["Philosophy & Mindfulness", "Psychology"],
            "goals": ["Personal Growth", "Mindfulness"],
            "styles": ["Psychological", "Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 32,
        "volumeInfo": {
            "title": "Meditations",
            "authors": ["Marcus Aurelius"],
            "description": "A collection of reflections on self-discipline, resilience, virtue, and living with purpose.",
            "isbn": "9780140449334",
            "publishedDate": "180",
            "publisher": "Penguin Classics",
            "pageCount": 304,
            "rating": 4.6,
            "categories": ["Philosophy & Mindfulness"],
            "goals": ["Personal Growth", "Mindfulness"],
            "styles": ["Psychological", "Detailed"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 33,
        "volumeInfo": {
            "title": "The Happiness Trap",
            "authors": ["Russ Harris"],
            "description": "A practical introduction to psychological flexibility, mindfulness, and handling difficult thoughts and emotions.",
            "isbn": "9781590305843",
            "publishedDate": "2007",
            "publisher": "Trumpeter",
            "pageCount": 272,
            "rating": 4.5,
            "categories": ["Philosophy & Mindfulness", "Psychology"],
            "goals": ["Personal Growth", "Mindfulness"],
            "styles": ["Psychological", "Practical"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 34,
        "volumeInfo": {
            "title": "The Gene",
            "authors": ["Siddhartha Mukherjee"],
            "description": "An accessible history and exploration of genetics, heredity, and the science of genes.",
            "isbn": "9781476733524",
            "publishedDate": "2016",
            "publisher": "Scribner",
            "pageCount": 608,
            "rating": 4.6,
            "categories": ["Science"],
            "goals": ["Study & Learning"],
            "styles": ["Detailed"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 35,
        "volumeInfo": {
            "title": "Astrophysics for People in a Hurry",
            "authors": ["Neil deGrasse Tyson"],
            "description": "A concise introduction to major ideas in astrophysics and our understanding of the universe.",
            "isbn": "9780393609394",
            "publishedDate": "2017",
            "publisher": "W. W. Norton",
            "pageCount": 224,
            "rating": 4.6,
            "categories": ["Science"],
            "goals": ["Study & Learning"],
            "styles": ["Practical", "Detailed"],
            "experiences": ["Beginner", "Quick"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 36,
        "volumeInfo": {
            "title": "The Creative Act",
            "authors": ["Rick Rubin"],
            "description": "A reflection on creativity, artistic practice, attention, and the process of making meaningful work.",
            "isbn": "9780593652886",
            "publishedDate": "2023",
            "publisher": "Penguin Press",
            "pageCount": 432,
            "rating": 4.5,
            "categories": ["Creativity & Writing"],
            "goals": ["Personal Growth"],
            "styles": ["Inspirational", "Detailed"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 37,
        "volumeInfo": {
            "title": "Bird by Bird",
            "authors": ["Anne Lamott"],
            "description": "A practical and encouraging guide to writing, creativity, and developing a regular writing practice.",
            "isbn": "9780385480017",
            "publishedDate": "1994",
            "publisher": "Pantheon",
            "pageCount": 256,
            "rating": 4.6,
            "categories": ["Creativity & Writing"],
            "goals": ["Personal Growth", "Study & Learning"],
            "styles": ["Practical", "Inspirational"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 38,
        "volumeInfo": {
            "title": "The Elements of Style",
            "authors": ["William Strunk Jr.", "E. B. White"],
            "description": "A concise guide to the principles of clear and effective English writing.",
            "isbn": "9780205309023",
            "publishedDate": "1918",
            "publisher": "Pearson",
            "pageCount": 105,
            "rating": 4.5,
            "categories": ["Creativity & Writing", "Education & Learning"],
            "goals": ["Study & Learning"],
            "styles": ["Practical"],
            "experiences": ["Beginner", "Quick"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 39,
        "volumeInfo": {
            "title": "The 7 Habits of Highly Effective People Workbook",
            "authors": ["Stephen R. Covey"],
            "description": "A practical companion for applying principles of personal effectiveness, communication, and leadership.",
            "isbn": "9780743268165",
            "publishedDate": "2003",
            "publisher": "Simon & Schuster",
            "pageCount": 288,
            "rating": 4.4,
            "categories": ["Career & Success", "Communication", "Education & Learning"],
            "goals": ["Career & Success", "Communication", "Study & Learning"],
            "styles": ["Practical"],
            "experiences": ["Beginner", "Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    },

    {
        "id": 40,
        "volumeInfo": {
            "title": "So Good They Can't Ignore You",
            "authors": ["Cal Newport"],
            "description": "An exploration of career development, skill building, and creating meaningful professional work.",
            "isbn": "9781455509126",
            "publishedDate": "2012",
            "publisher": "Grand Central Publishing",
            "pageCount": 288, 
            "rating": 4.5,
            "categories": ["Career & Success", "Personal Growth"],
            "goals": ["Career & Success", "Personal Growth"],
            "styles": ["Practical"],
            "experiences": ["Detailed"],
            "infoLink": "https://books.google.com/books"
        }
    }
]
# Load additional books from books_data.json

with open("books_data.json", "r", encoding="utf-8") as file:
    additional_books = json.load(file)

backup_books.extend(additional_books)

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return "Please fill all fields."

        hashed_password = generate_password_hash(password)

        try:

            connection = sqlite3.connect("database/bookdiscovery.db")

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, hashed_password))

            connection.commit()
            connection.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            return "This email is already registered."

    return render_template("register.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        connection = sqlite3.connect("database/bookdiscovery.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, name, password FROM users WHERE email = ?",
            (email,)
        )

        user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(user[2], password):

            session["user_id"] = user[0]
            session["user_name"] = user[1]

            return redirect(url_for("home"))

        return "Invalid email or password."

    return render_template("login.html")
@app.route("/favorite/<int:book_id>")
def favorite(book_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    connection = sqlite3.connect("database/bookdiscovery.db")

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id FROM favorites
        WHERE user_id = ? AND book_id = ?
        """,
        (user_id, book_id)
    )

    existing_favorite = cursor.fetchone()

    if not existing_favorite:

        cursor.execute(
            """
            INSERT INTO favorites (user_id, book_id)
            VALUES (?, ?)
            """,
            (user_id, book_id)
        )

        connection.commit()

    connection.close()

    return redirect(request.referrer or url_for("home"))

@app.route("/remove-favorite/<int:book_id>")
def remove_favorite(book_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    connection = sqlite3.connect("database/bookdiscovery.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM favorites
        WHERE user_id = ? AND book_id = ?
        """,
        (user_id, book_id)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("favorites"))

@app.route("/favorites")
def favorites():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    connection = sqlite3.connect("database/bookdiscovery.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT book_id FROM favorites WHERE user_id = ?",
        (user_id,)
    )

    favorite_rows = cursor.fetchall()

    connection.close()

    favorite_ids = [row[0] for row in favorite_rows]

    favorite_books = [
        book for book in backup_books
        if book["id"] in favorite_ids
    ]

    return render_template(
        "favorites.html",
        books=favorite_books
    )


@app.route("/search")
def search():

    query = request.args.get("q", "").strip()

    if not query:
        return render_template(
            "results.html",
            books=[],
            query="",
            error="Please enter a book title, author, or keyword to search."
        )

    api_url = "https://www.googleapis.com/books/v1/volumes"

    params = {
        "q": query,
        "maxResults": 12
    }

    books = []

    try:
        response = requests.get(
            api_url,
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            books = data.get("items", [])

    except requests.RequestException as error:
        print("API Error:", error)

    # Use backup books if API is unavailable
    if not books:

        query_lower = query.lower()

        books = [
            book for book in backup_books
            if query_lower in book["volumeInfo"]["title"].lower()
            or any(
                query_lower in author.lower()
                for author in book["volumeInfo"].get("authors", [])
            )
        ]

    

    # Check which books are already in Favorites
    favorite_ids = set()

    if session.get("user_id"):

        connection = sqlite3.connect("database/bookdiscovery.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT book_id FROM favorites
            WHERE user_id = ?
            """,
            (session.get("user_id"),)
        )

        favorite_ids = {row[0] for row in cursor.fetchall()}

        connection.close()

    return render_template(
        "results.html",
        books=books,
        query=query,
        favorite_ids=favorite_ids
    )

@app.route("/category/<category_name>")
def category(category_name):

    category_books = [
        book for book in backup_books
        if any(
            category_name.lower() in category.lower()
            for category in book["volumeInfo"].get("categories", [])
        )
    ]

    # Check which books are already in Favorites
    favorite_ids = set()

    if session.get("user_id"):

        connection = sqlite3.connect("database/bookdiscovery.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT book_id FROM favorites
            WHERE user_id = ?
            """,
            (session.get("user_id"),)
        )

        favorite_ids = {row[0] for row in cursor.fetchall()}

        connection.close()

    return render_template(
        "results.html",
        books=category_books,
        query=category_name,
        favorite_ids=favorite_ids
    )
@app.route("/goal/<goal_name>")
def goal(goal_name):

    goal_books = [
        book for book in backup_books
        if any(
            goal_name.lower() == goal.lower()
            for goal in book["volumeInfo"].get("goals", [])
        )
    ]

    # Check which books are already in Favorites
    favorite_ids = set()

    if session.get("user_id"):

        connection = sqlite3.connect("database/bookdiscovery.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT book_id FROM favorites
            WHERE user_id = ?
            """,
            (session.get("user_id"),)
        )

        favorite_ids = {row[0] for row in cursor.fetchall()}

        connection.close()

    return render_template(
        "results.html",
        books=goal_books,
        query=goal_name,
        favorite_ids=favorite_ids
    )

@app.route("/quick-pick")
def quick_pick():

    goal_name = request.args.get("goal")
    style_name = request.args.get("style")
    experience_name = request.args.get("experience")

    if not goal_name:
        return render_template("quick_pick.html")

    recommended_books = []

    for book in backup_books:

        book_info = book["volumeInfo"]

        goals = book_info.get("goals", [])
        styles = book_info.get("styles", [])
        experiences = book_info.get("experiences", [])

        if goal_name.lower() not in [
            goal.lower() for goal in goals
        ]:
            continue

        score = 3

        if style_name and any(
            style_name.lower() == style.lower()
            for style in styles
        ):
            score += 2

        if experience_name and any(
            experience_name.lower() == experience.lower()
            for experience in experiences
        ):
            score += 1

        recommended_books.append((score, book))

    recommended_books.sort(
        key=lambda item: item[0],
        reverse=True
    )

    books = [
    book for score, book in recommended_books[:10]
]

    # Check which books are already in Favorites
    favorite_ids = set()

    if session.get("user_id"):

        connection = sqlite3.connect("database/bookdiscovery.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT book_id FROM favorites
            WHERE user_id = ?
            """,
            (session.get("user_id"),)
        )

        favorite_ids = {row[0] for row in cursor.fetchall()}

        connection.close()

    return render_template(
        "results.html",
        books=books,
        query="Quick Pick: " + goal_name,
        favorite_ids=favorite_ids
    )

@app.route("/book/<int:book_id>")
def book_details(book_id):

    book = next(
        (book for book in backup_books if book.get("id") == book_id),
        None
    )

    if book is None:
        return "Book not found", 404

    # Record book in history for logged-in users
    if session.get("user_id"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(
            base_dir,
            "database",
            "bookdiscovery.db"
        )

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        # Remove previous entry so the latest visit appears first
        cursor.execute(
            "DELETE FROM history WHERE user_id = ? AND book_id = ?",
            (session["user_id"], book_id)
        )

        cursor.execute(
            "INSERT INTO history (user_id, book_id) VALUES (?, ?)",
            (session["user_id"], book_id)
        )

        connection.commit()
        connection.close()

    return render_template(
        "book_details.html",
        book=book
    )
@app.route("/history")
def history():

    if not session.get("user_id"):
        return redirect("/login")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(
        base_dir,
        "database",
        "bookdiscovery.db"
    )

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT book_id
        FROM history
        WHERE user_id = ?
        ORDER BY viewed_at DESC
    """, (session["user_id"],))

    history_rows = cursor.fetchall()

    connection.close()

    history_books = []

    for row in history_rows:

        book_id = row[0]

        book = next(
            (book for book in backup_books if book.get("id") == book_id),
            None
        )

        if book:
            history_books.append(book)

    return render_template(
        "history.html",
        books=history_books
    )




if __name__ == "__main__":
    init_db()
    app.run(debug=True)