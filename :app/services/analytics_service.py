from ..database import database
from ..models import books, reading_progress, notes
from ..schemas import UserAnalytics


async def compute_user_analytics(user_id: int):
    query = books.select().where(books.c.user_id == user_id)
    user_books = await database.fetch_all(query)

    total_books = len(user_books)

    progress_query = reading_progress.select().where(
        reading_progress.c.book_id.in_([b["id"] for b in user_books])
    )
    progress_entries = await database.fetch_all(progress_query)

    total_pages_read = sum(p["pages_read"] for p in progress_entries)
    avg_speed = total_pages_read / len(progress_entries) if progress_entries else 0.0

    genres = [b["genre"] for b in user_books if b["genre"]]
    top_genre = max(set(genres), key=genres.count) if genres else None

    active_days = sorted({p["date"].strftime("%A") for p in progress_entries})

    notes_query = notes.select().where(
        notes.c.book_id.in_([b["id"] for b in user_books])
    )
    notes_entries = await database.fetch_all(notes_query)

    keywords = []
    for n in notes_entries:
        for word in n["note"].split():
            if len(word) > 4:
                keywords.append(word.lower())

    top_keywords = list(set(keywords))

    return UserAnalytics(
        user_id=user_id,
        total_books=total_books,
        total_pages_read=total_pages_read,
        avg_speed=round(avg_speed, 2),
        top_genre=top_genre,
        active_days=active_days,
        keywords=top_keywords
    )


