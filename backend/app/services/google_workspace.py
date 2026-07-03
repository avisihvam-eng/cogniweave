import os
import csv
import datetime
from app.config import settings

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    GOOGLE_CLIENTS_AVAILABLE = True
except ImportError:
    GOOGLE_CLIENTS_AVAILABLE = False

# Helper to format document text
def format_analysis_doc(data: dict) -> str:
    lines = []
    lines.append("=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*")
    lines.append("ANTIGRAVITY KNOWLEDGE COMPILATION")
    lines.append("=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*\n")
    lines.append(f"Title: {data.get('title', 'Untitled')}")
    lines.append(f"Speaker: {data.get('speaker', 'Unknown')}")
    lines.append(f"Source: {data.get('source', 'Unknown')} ({data.get('url', 'N/A')})")
    lines.append(f"Date Ingested: {datetime.date.today().isoformat()}\n")
    
    lines.append("## Core Thesis")
    lines.append(data.get('core_thesis', 'No thesis extracted.') + "\n")
    
    lines.append("## Highest Signal Insights")
    for i, ins in enumerate(data.get('insights', []), 1):
        lines.append(f"{i}. {ins.get('insight', '')}")
        lines.append(f"   - Why it Matters: {ins.get('why_it_matters', '')}")
        lines.append(f"   - Application: {ins.get('application', '')}")
        lines.append(f"   - Action: {ins.get('action', '')}\n")
        
    lines.append("## Mental Models")
    for mm in data.get('mental_models', []):
        lines.append(f"- {mm.get('name', '')}: {mm.get('definition', '')}")
        lines.append(f"  - Explanation: {mm.get('explanation', '')}")
        lines.append(f"  - Example: {mm.get('example', '')}")
        lines.append(f"  - Application: {mm.get('application', '')}\n")

    lines.append("## Vocabulary")
    for v in data.get('vocabulary', []):
        lines.append(f"- {v.get('word', '')}: {v.get('meaning', '')}")
        lines.append(f"  - Origin: {v.get('origin', '')}")
        lines.append(f"  - Usage: {v.get('usage', '')}")
        lines.append(f"  - Simpler Synonym: {v.get('simpler_synonym', '')}\n")

    lines.append("## Quotes")
    for q in data.get('quotes', []):
        lines.append(f'> "{q.get("quote", "")}"')
        lines.append(f"  - Meaning: {q.get('meaning', '')}")
        lines.append(f"  - Why Memorable: {q.get('why_memorable', '')}")
        lines.append(f"  - Counterargument: {q.get('counterargument', '')}\n")
        
    lines.append("## Contrarian Perspective")
    cp = data.get('contrarian', {})
    lines.append(f"- Opposing Argument: {cp.get('opposing_argument', '')}")
    lines.append(f"- Assumptions Challenged: {cp.get('assumptions', '')}")
    lines.append(f"- Evidence Missing: {cp.get('evidence_missing', '')}")
    lines.append(f"- Confidence Score: {cp.get('confidence_score', '')}/10\n")
    
    lines.append("## Content Assets")
    assets = data.get('content_assets', {})
    lines.append("### Tweets")
    for t in assets.get('tweets', []):
        lines.append(f"- {t}")
    lines.append(f"\n### LinkedIn Post\n{assets.get('linkedin_post', '')}\n")
    lines.append(f"### Newsletter Outline\n{assets.get('newsletter_outline', '')}\n")

    return "\n".join(lines)

class GoogleWorkspaceService:
    def __init__(self, creds_data=None):
        self.creds_data = creds_data
        self.use_local = True
        
        if creds_data and GOOGLE_CLIENTS_AVAILABLE:
            try:
                self.creds = Credentials.from_authorized_user_info(creds_data)
                self.drive_service = build('drive', 'v3', credentials=self.creds)
                self.docs_service = build('docs', 'v1', credentials=self.creds)
                self.sheets_service = build('sheets', 'v4', credentials=self.creds)
                self.use_local = False
            except Exception as e:
                print(f"Failed to initialize Google API clients: {e}. Defaulting to Local Workspace.")
                
        if self.use_local:
            self.local_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'local_drive'))
            os.makedirs(self.local_root, exist_ok=True)
            print(f"Running Google Workspace Service in LOCAL mode. Saving to {self.local_root}")

    async def save_compilation(self, data: dict, category: str) -> str:
        """
        Saves analysis compilation. Returns URL link (Google Doc URL or Local File Path).
        """
        doc_title = f"{data.get('title', 'Untitled')} - Analysis"
        doc_content = format_analysis_doc(data)
        
        if not self.use_local:
            try:
                # 1. Find or create root folder "Antigravity"
                root_id = self._get_or_create_folder(settings.DRIVE_ROOT_FOLDER)
                # 2. Find or create category folder inside root
                cat_id = self._get_or_create_folder(category, parent_id=root_id)
                # 3. Find or create year folder inside category
                year = str(datetime.date.today().year)
                year_id = self._get_or_create_folder(year, parent_id=cat_id)
                
                # 4. Create Google Doc
                doc = self.docs_service.documents().create(body={'title': doc_title}).execute()
                doc_id = doc.get('documentId')
                
                # 5. Move to year folder
                self.drive_service.files().update(
                    fileId=doc_id,
                    addParents=year_id,
                    removeParents='root',
                    fields='id, parents'
                ).execute()
                
                # 6. Populate text content
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={
                        'requests': [
                            {
                                'insertText': {
                                    'location': {'index': 1},
                                    'text': doc_content
                                }
                            }
                        ]
                    }
                ).execute()
                
                doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
                await self.update_sheets_database(data, doc_link)
                return doc_link
            except Exception as e:
                print(f"Error saving to Google Drive: {e}. Saving locally instead.")
                self.use_local = True
                # Fallthrough to local saving
                
        if self.use_local:
            year = str(datetime.date.today().year)
            folder_path = os.path.join(self.local_root, category, year)
            os.makedirs(folder_path, exist_ok=True)
            
            # Clean title for filename
            safe_title = "".join([c if c.isalnum() or c in (' ', '_', '-') else '' for c in data.get('title', 'Untitled')]).strip()
            file_path = os.path.join(folder_path, f"{safe_title}.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            doc_link = f"file:///{file_path.replace(os.sep, '/')}"
            await self.update_sheets_database(data, doc_link)
            return doc_link

    async def update_sheets_database(self, data: dict, doc_link: str):
        """
        Appends or updates a row in the Google Sheets Master Index (or local CSV).
        """
        date_str = datetime.date.today().isoformat()
        row_data = [
            date_str,
            data.get('title', 'Untitled'),
            data.get('source', 'Unknown'),
            data.get('speaker', 'Unknown'),
            str(data.get('duration', 0)),
            ', '.join(data.get('topics', [])),
            data.get('url', ''),
            data.get('core_thesis', '')[:100] + '...',
            data.get('insights', [{}])[0].get('insight', '') if data.get('insights') else '',
            data.get('quotes', [{}])[0].get('quote', '') if data.get('quotes') else '',
            ', '.join([m.get('name') for m in data.get('mental_models', []) if m.get('name')]),
            str(len(data.get('vocabulary', []))),
            '; '.join([a.get('action') for a in data.get('insights', []) if a.get('action')]),
            '; '.join(data.get('content_assets', {}).get('tweets', [])),
            ', '.join(data.get('reading_list', [])),
            doc_link,
            'Ingested',
            str(data.get('personal_rating', 0)),
            date_str
        ]
        
        if not self.use_local:
            try:
                # Google Sheets implementation
                sheet_id = self._get_or_create_sheet("Antigravity Master Index")
                self.sheets_service.spreadsheets().values().append(
                    spreadsheetId=sheet_id,
                    range="A:S",
                    valueInputOption="USER_ENTERED",
                    body={'values': [row_data]}
                ).execute()
                return
            except Exception as e:
                print(f"Error updating Google Sheets database: {e}. Fallback to local CSV.")
                self.use_local = True
                
        if self.use_local:
            csv_path = os.path.join(self.local_root, 'master_index.csv')
            headers = [
                'Date', 'Title', 'Source', 'Speaker', 'Duration', 'Topics', 'URL', 
                'Core Thesis', 'Top Insight', 'Best Quote', 'Mental Models', 'Vocabulary Count',
                'Actions', 'Tweets', 'Reading List', 'Google Doc Link', 'Status', 'Personal Rating', 'Review Date'
            ]
            
            write_headers = not os.path.exists(csv_path)
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if write_headers:
                    writer.writerow(headers)
                writer.writerow(row_data)

    def _get_or_create_folder(self, name: str, parent_id: str = None) -> str:
        query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        results = self.drive_service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
            
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

    def _get_or_create_sheet(self, name: str) -> str:
        root_id = self._get_or_create_folder(settings.DRIVE_ROOT_FOLDER)
        query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false and '{root_id}' in parents"
        results = self.drive_service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
            
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [root_id]
        }
        spreadsheet = self.drive_service.files().create(body=file_metadata, fields='id').execute()
        sheet_id = spreadsheet.get('id')
        
        # Add headers to the new sheet
        headers = [
            'Date', 'Title', 'Source', 'Speaker', 'Duration', 'Topics', 'URL', 
            'Core Thesis', 'Top Insight', 'Best Quote', 'Mental Models', 'Vocabulary Count',
            'Actions', 'Tweets', 'Reading List', 'Google Doc Link', 'Status', 'Personal Rating', 'Review Date'
        ]
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="A1:S1",
            valueInputOption="RAW",
            body={'values': [headers]}
        ).execute()
        
        return sheet_id
