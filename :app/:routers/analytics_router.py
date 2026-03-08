from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import database
from ..models import books, reading_progress, notes
from ..schemas import BookAnalytics, UserAnalytics, StreakOut, ReadingSpeed, FinishDate,Recommendation
from .auth_router import get_current_user
from ..services.analytics_service import compute_user_analytics
from ..services.cache_service import get_cache,set_cache

router = APIRouter()

@router.get("/books/{book_id}/analytics",response_model=BookAnalytics)
async def get_book_analytics(book_id:int,current_user=Depends(get_current_user)):
    query=books.select().where((books.c.id==book_id) & (books.c.user_id==current_user["id"]))
    book = await database.fetch_one(query)
    if not book:
        raise HTTPException(404,"Book not borrowed hence analytics can't be given")
    
    progress_query=(
        reading_progress.select().with_only_columns(
            func.sum(reading_progress.c.pages_read).label("pages_read"),
            func.count(reading_progress.c.id).label("sessions"),
            func.max(reading_progress.c.date).label("last_read")
            ).where(reading_progress.c.book_id==book_id))
    result=await database.fetch_one(progress_query)
    if not result:
        return BookAnalytics(book_id=book_id,
                         title=book["title"],
                         total_pages=book["total_pages"],
                         pages_read=0,
                         progress_percent=0.0,
                         sessions=0,
                         last_read=None)
    pages_read=result["pages_read"]
    sessions=result["sessions"]
    last_read=result["last_read"]
    
    if book["total_pages"]:
        percent= round((pages_read/book["total_pages"])*100,2)
    else:
        percent=0.0
    
    return BookAnalytics(book_id=book_id,
                         title=book["title"],
                         total_pages=book["total_pages"],
                         pages_read=pages_read,
                         progress_percent=percent,
                         sessions=sessions,
                         last_read=last_read)

@router.get("/books/{book_id}/streaks",response_model=StreakOut)
async def get_streaks(book_id:int,current_user=Depends(get_current_user)):
    query=books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    book = await database.fetch_one(query)
    if not book:
        raise HTTPException(404,"Book not borrowed hence no streak")
    dates_query=reading_progress.select().with_only_columns(
        reading_progress.c.date).where(reading_progress.c.book_id==book_id).order_by(reading_progress.c.date.desc())
    data=await database.fetch_all(dates_query)
    if not data:
        return StreakOut(book_id=book_id,current_streak=0,longest_streak=0)
     
    dates= [row["date"].date() for row in data]
    
    unique_dates=sorted(set(dates),reverse=True)
    today=datetime.utcnow().date()
    streak=0
    
    for i,d in enumerate(unique_dates):
        if i==0:
            if d == today:
                streak=1
            elif d==today-timedelta(days=1):
                streak = 1
            else:
                streak =0
                break
        else:
             if d==unique_dates[i-1]-timedelta(days=1):
                 streak += 1
             else:
                 break
            
    longest = 1
    current = 1
    for i in range(1,len(unique_dates)):
        if unique_dates[i]==unique_dates[i-1]-timedelta(days=1):
            current+=1
            longest = max(longest,current)
        else:
            current=1
            
    return StreakOut(
        book_id=book_id,
        current_streak=streak,
        longest_streak=longest)





@router.get("/analytics/user",response_model=UserAnalytics)
async def get_user_analytics(current_user=Depends(get_current_user)):
    cache_key=f"user_analytics:{current_user['id']}"
    cached = await get_cache(cache_key)
    if cached:
        return cached
    
    analytics = await compute_user_analytics(current_user["id"])
    await set_cache(cache_key,analytics.dict(),ttl=120)
    return analytics


@router.get("/recommendations", response_model=list[Recommendation])
async def get_recommendations(current_user = Depends(get_current_user)):
    # Get user analytics
    cache_key=f"recommendations:{current_user['id']}"
    cached = await get_cache(cache_key)
    if cached:
        return cached
    
    analytics = await compute_user_analytics(current_user["id"])

    recs = []

    # 1. Genre-based recommendation
    if analytics.top_genre:
        recs.append(Recommendation(
            reason=f"You read a lot of {analytics.top_genre}",
            suggestion=f"Try exploring more books in {analytics.top_genre}"
        ))

    # 2. Speed-based recommendation
    if analytics.avg_speed > 20:
        recs.append(Recommendation(
            reason="You read quickly",
            suggestion="Consider longer or more complex books"
        ))
    else:
        recs.append(Recommendation(
            reason="Your reading pace is relaxed",
            suggestion="Shorter books or novellas might feel more rewarding"
        ))

    # 3. Active day recommendation
    if analytics.active_days:
        recs.append(Recommendation(
            reason=f"You read most on {', '.join(analytics.active_days)}",
            suggestion="Schedule reading sessions on those days to build streaks"
        ))

    # 4. Keyword-based recommendation
    if analytics.keywords:
        keyword = analytics.keywords[0]
        recs.append(Recommendation(
            reason=f"You often write notes about '{keyword}'",
            suggestion=f"Look for books that explore themes related to '{keyword}'"
        ))
    await set_cache(cache_key,[r.dict() for r in recs],ttl=120)
    return recs


@router.get("/books/{book_id}/speed",response_model=ReadingSpeed)
async def get_reading_speed(book_id:int,current_user=Depends(get_current_user)):
    query=books.select().where((books.c.id==book_id) & (books.c.user_id==current_user["id"]))
    book=await database.fetch_one(query)
    if not book:
           raise HTTPException(404,"Book not found")
    progress_query=reading_progress.select().where(reading_progress.c.book_id==book["id"])
    
    entries=await database.fetch_all(progress_query)
    if not entries:
            return ReadingSpeed(book_id=book_id,pages_per_session=0.0,pages_per_day=0.0)
    
    total_pages = sum(p["pages_read"] for p in entries)
    sessions = len(entries)
    pps = total_pages/sessions
    unique_days= {e["date"].date() for e in entries}
    total_days = len(unique_days)
    ppd=total_pages/total_days
    return ReadingSpeed(
        book_id=book_id,pages_per_session=round(pps,2),pages_per_day=round(ppd,2))
                               
    
@router.get("/books/{book_id}/finish_date",response_model=FinishDate)
async def get_finish_date(book_id:int,current_user=Depends(get_current_user)):
    query=books.select().where((books.c.id==book_id) & (books.c.user_id==current_user["id"]))
    book=await database.fetch_one(query)
    if not book:
           raise HTTPException(404,"Book not found")
    if not book["total_pages"]:
            raise HTTPException(400, "Book must have total_pages to estimate finish date")
    total_pages = book["total_pages"]
    progress_query=reading_progress.select().where(reading_progress.c.book_id==book["id"])
    entries=await database.fetch_all(progress_query)
    if not entries:
            return FinishDate(book_id=book_id,remaining_pages=total_pages,
                              pages_per_day=0.0,finish_date=None)
                               
    pages_read=sum(p["pages_read"] for p in entries)
    remaining_pages=total_pages-pages_read
    unique_days= {e["date"].date() for e in entries}
    total_days = len(unique_days)
    ppd=total_pages/total_days
    if ppd == 0:
        return FinishDate( book_id=book_id,
                           remaining_pages=remaining_pages,
                           pages_per_day=0.0,
                           finish_date=None ) 
    
    days_remaining=remaining_pages/ppd
    today=datetime.utcnow()
    finish_date=today+timedelta(days=days_remaining)
    return FinishDate(book_id=book_id,remaining_pages=remaining_pages,
                      pages_per_day=ppd, finish_date=finish_date)
    
    

