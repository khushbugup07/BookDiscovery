import json
import requests
import time


# ==========================================
# BookDiscovery - Popular Book Dataset
# ==========================================

categories = {
    "Self-Help": [
        "self help",
        "personal development",
        "habits",
        "productivity"
    ],

    "Psychology": [
        "psychology",
        "human behavior",
        "cognitive psychology"
    ],

    "Business": [
        "business",
        "entrepreneurship",
        "startups",
        "management"
    ],

    "Finance": [
        "personal finance",
        "investing",
        "financial literacy",
        "money"
    ],

    "Personal Growth": [
        "personal growth",
        "self improvement",
        "motivation",
        "mindset"
    ],

    "Education & Learning": [
        "learning",
        "education",
        "study skills",
        "learning how to learn"
    ],

    "Communication": [
        "communication",
        "public speaking",
        "conversation",
        "relationships"
    ],

    "Career & Success": [
        "career",
        "success",
        "professional development",
        "work"
    ],

    "Biography": [
        "biography",
        "autobiography",
        "memoir",
        "famous people"
    ],

    "Philosophy & Mindfulness": [
        "philosophy",
        "mindfulness",
        "meditation",
        "stoicism"
    ],

    "Science": [
        "popular science",
        "physics",
        "biology",
        "astronomy"
    ],

    "Creativity & Writing": [
        "writing",
        "creativity",
        "creative writing",
        "art"
    ]
}


# ==========================================
# Original 40 book titles
# These will NOT be added again
# ==========================================

original_titles = {
    "atomic habits",
    "the 7 habits of highly effective people",
    "think and grow rich",
    "the power of now",
    "how to win friends and influence people",
    "the psychology of money",
    "the power of habit",
    "the lean startup",
    "rich dad poor dad",
    "mindset",
    "deep work",
    "how to talk to anyone",
    "the 5 am club",
    "the subtle art of not giving a f*ck",
    "zero to one",
    "the intelligent investor",
    "quiet",
    "the 48 laws of power",
    "steve jobs",
    "the diary of a young girl",
    "the art of happiness",
    "the book of joy",
    "a brief history of time",
    "cosmos",
    "the selfish gene",
    "on writing well",
    "big magic",
    "steal like an artist",
    "leonardo da vinci",
    "becoming",
    "man's search for meaning",
    "meditations",
    "the happiness trap",
    "the gene",
    "astrophysics for people in a hurry",
    "the creative act",
    "bird by bird",
    "the elements of style",
    "the 7 habits of highly effective people workbook",
    "so good they can't ignore you"
}


def get_goals(category):

    mapping = {
        "Self-Help": ["Personal Growth"],
        "Psychology": ["Personal Growth"],
        "Business": ["Career & Success"],
        "Finance": ["Finance"],
        "Personal Growth": ["Personal Growth"],
        "Education & Learning": ["Study & Learning"],
        "Communication": ["Communication"],
        "Career & Success": ["Career & Success"],
        "Biography": ["Personal Growth"],
        "Philosophy & Mindfulness": ["Personal Growth"],
        "Science": ["Study & Learning"],
        "Creativity & Writing": ["Personal Growth"]
    }

    return mapping.get(
        category,
        ["Personal Growth"]
    )


def get_style(category):

    if category in [
        "Business",
        "Finance",
        "Education & Learning",
        "Career & Success"
    ]:
        return ["Practical"]

    if category in [
        "Biography",
        "Personal Growth",
        "Philosophy & Mindfulness"
    ]:
        return ["Inspirational"]

    return ["Practical"]


def get_experience(category):

    if category in [
        "Science",
        "Psychology",
        "Philosophy & Mindfulness"
    ]:
        return ["Detailed"]

    return ["Beginner-Friendly"]


def clean_description(description):

    if isinstance(description, dict):
        description = description.get(
            "value",
            ""
        )

    if isinstance(description, list):
        description = " ".join(
            str(item)
            for item in description
        )

    if not description:
        return ""

    return str(description).strip()


# ==========================================
# Generate books
# ==========================================

books = []

seen_titles = set()

next_id = 41


for category, queries in categories.items():

    print()
    print("=" * 50)
    print("Category:", category)
    print("=" * 50)

    category_books = []

    for query in queries:

        if len(category_books) >= 47:
            break

        print("Searching:", query)

        url = "https://openlibrary.org/search.json"

        params = {
            "q": query,
            "language": "eng",
            "limit": 100,
            "fields": (
                "key,title,author_name,first_publish_year,"
                "isbn,cover_i,number_of_pages_median,"
                "ratings_average,publisher,description"
            )
        }

        try:

            response = requests.get(
                url,
                params=params,
                timeout=30
            )

            if response.status_code != 200:

                print(
                    "Request failed:",
                    response.status_code
                )

                continue

            data = response.json()

        except requests.RequestException as error:

            print(
                "Network error:",
                error
            )

            continue

        for document in data.get(
            "docs",
            []
        ):

            if len(category_books) >= 47:
                break

            title = document.get("title")

            authors = document.get(
                "author_name",
                []
            )

            description = clean_description(
                document.get("description")
            )

            cover_id = document.get(
                "cover_i"
            )

            # Must have title
            if not title:
                continue

            # Must have author
            if not authors:
                continue

            # Must have description
            if not description:
                continue

            # Must have cover
            if not cover_id:
                continue

            title_key = title.lower().strip()

            # Skip original 40 books
            if title_key in original_titles:
                continue

            # Skip duplicate titles
            if title_key in seen_titles:
                continue

            seen_titles.add(title_key)

            isbn_list = document.get(
                "isbn",
                []
            )

            isbn = ""

            if isbn_list:
                isbn = isbn_list[0]

            publisher_list = document.get(
                "publisher",
                []
            )

            publisher = ""

            if publisher_list:
                publisher = publisher_list[0]

            year = document.get(
                "first_publish_year"
            )

            pages = document.get(
                "number_of_pages_median"
            )

            rating = document.get(
                "ratings_average"
            )

            cover_url = (
                "https://covers.openlibrary.org/"
                f"b/id/{cover_id}-L.jpg"
            )

            book = {
                "id": next_id,

                "volumeInfo": {

                    "title": title,

                    "authors": authors,

                    "description": description,

                    "isbn": isbn,

                    "publishedDate": (
                        str(year)
                        if year
                        else ""
                    ),

                    "publisher": publisher,

                    "pageCount": (
                        pages
                        if pages
                        else 0
                    ),

                    "rating": (
                        round(
                            rating,
                            1
                        )
                        if isinstance(
                            rating,
                            (int, float)
                        )
                        else 0
                    ),

                    "categories": [
                        category
                    ],

                    "goals": get_goals(
                        category
                    ),

                    "styles": get_style(
                        category
                    ),

                    "experiences": get_experience(
                        category
                    ),

                    "infoLink": (
                        "https://openlibrary.org"
                        + document.get(
                            "key",
                            ""
                        )
                    ),

                    "imageLinks": {
                        "thumbnail": cover_url
                    }
                }
            }

            books.append(book)

            category_books.append(book)

            next_id += 1

        time.sleep(1)

    print(
        f"{category}: "
        f"{len(category_books)} books accepted"
    )


# ==========================================
# Save dataset
# ==========================================

with open(
    "books_data.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        books,
        file,
        indent=4,
        ensure_ascii=False
    )


print()
print("=" * 50)
print("DATASET GENERATION COMPLETE")
print("=" * 50)
print("Additional books:", len(books))
print("Original books:", 40)
print("Approximate total:", 40 + len(books))
print("=" * 50)