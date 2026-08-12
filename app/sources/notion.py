from notion_client import Client

from app.core.config import settings
from app.schemas.knowledge import KnowledgeDocument

client = Client(auth=settings.notion_api_key)

def extract_rich_text(rich_text: list[dict]) -> str:
    return "".join(
        item["plain_text"] for item in rich_text
    )

def extract_block_text(block:dict) -> str:
    block_type = block["type"]

    block_data = block.get(block_type, {})
    rich_text = block_data.get("rich_text", [])

    return extract_rich_text(rich_text=rich_text)

def get_block_children(block_id: str) -> list[dict]:
    results = []
  
    response = client.blocks.children.list(
        block_id=block_id
    )

    results.extend(response["results"])

    #check if there are pagination
    while response["has_more"]:
        cursor = response["next_cursor"]
        response = client.blocks.children.list(
            block_id=block_id,
            start_cursor=cursor
        )
        results.extend(response["results"])

    return results

def extract_blocks_recursive(block_id: str) -> list[str]:
    parts = []

    blocks = get_block_children(block_id=block_id)

    for block in blocks:
        text = extract_block_text(block)

        if text:
            parts.append(text)

        if block["has_children"]:
            child_parts = extract_blocks_recursive(block["id"])
            parts.extend(child_parts)

    return parts

def extract_page_content(page_id: str) -> str:
    
    parts = extract_blocks_recursive(page_id)

    return "\n\n".join(parts)

def extract_page_title(page: dict) -> str:
    title_items = page["properties"]["title"]["title"]

    return "".join(
        item["plain_text"]
        for item in title_items
    )

def load_notion_page(page_id: str) -> KnowledgeDocument:
    #Get the notion page
    page = client.pages.retrieve(
        page_id= page_id
    )

    #extract title and content
    title = extract_page_title(page = page)
    content = extract_page_content (page_id= page["id"])

    document_id = page["id"]

    #create the metadata
    metadata = {
        "document_id": document_id,
        "source": f"notion://{page['id']}",
        "title": title,
        "source_type": "notion"
    }

    return KnowledgeDocument(
        document_id= document_id,
        content = content,
        metadata = metadata
    )

