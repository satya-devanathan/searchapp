
from fastapi import FastAPI, responses, BackgroundTasks
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import HTMLResponse

from Search import search_text, tasks_list_html, search_result
import starlette.status as status
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/search/", response_class=HTMLResponse)
async def search(request: Request):
    try:
        return templates.TemplateResponse("search.html", {"request": request, "tasks": tasks_list_html()})
    except Exception as ex:
        print(f"ERROR{ex}")


@app.post("/search/")
async def search(request: Request, background_tasks: BackgroundTasks):
    try:
        form_data = await request.form()
        search_string = form_data["query"].strip()
        if len(search_string.strip()) == 0:
            return responses.RedirectResponse('/search', status_code=status.HTTP_302_FOUND)

        background_tasks.add_task(search_text, search_string)

        return responses.RedirectResponse('/search', status_code=status.HTTP_302_FOUND)
    except Exception as ex:
        print(f"search->post: ERROR{ex}")


@app.get("/tasks/", response_class=HTMLResponse)
async def tasks():
    try:
        return "<html><body align=center>" + tasks_list_html() + "</body></html>"
    except Exception as ex:
        print(f"ERROR{ex}")


@app.get("/results/", response_class=HTMLResponse)
async def results(q: str):
    return search_result(q)
