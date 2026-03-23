# Product Requirements Document
## H-NoteBook — AI-Powered Web Notebook Application

| Field | Detail |
|---|---|
| Document Version | 1.0 |
| Status | Draft |
| Author | Product Management |
| Last Updated | 2026-03-23 |

---

## 1. Overview

### 1.1 Product Summary

H-NoteBook is a web-based notebook application that enables users to organise knowledge from multiple source types (web pages, documents, and plain text files) into discrete notebooks. Each notebook contains an integrated AI chatbot that answers questions strictly grounded in the imported sources. Users can also export their knowledge into various output formats directly from the notebook interface.

### 1.2 Problem Statement

Knowledge workers frequently juggle information from disparate sources — articles, internal documents, and notes — with no unified workspace to query and synthesise that information. Switching between browser tabs, document viewers, and AI tools introduces friction and increases the risk of answers that are not grounded in the user's specific content.

### 1.3 Goals

- Provide a clean, card-based notebook workspace that scales to many notebooks.
- Allow users to import heterogeneous sources into a notebook with minimal friction.
- Deliver a chatbot experience that is strictly grounded in the user's imported sources, supporting multi-source selection.
- Offer one-click export to common output formats (summary report, mind map, Word, PowerPoint, Excel).

### 1.4 Non-Goals

- Mobile native applications (iOS / Android) — the web app will be responsive but this is a web-only release.
- Real-time collaboration between multiple users.
- Source types beyond those listed in Section 4 (e.g., video, audio, spreadsheet import).

---

## 2. Target Users

| Persona | Description |
|---|---|
| Researcher / Analyst | Aggregates papers, URLs, and reports into a single notebook and interrogates the content with targeted questions. |
| Knowledge Worker | Organises project documents and generates summaries or presentations without leaving the application. |
| Student | Collects study materials and uses the chatbot to quiz themselves or generate study aids. |

---

## 3. User Stories

**Home Page**

- As a user, I want to see all my existing notebooks as visual cards so I can quickly identify and open the one I need.
- As a user, I want a prominent "Create New Notebook" card so I can start a new notebook in one click.

**Notebook Creation & Detail**

- As a user, I want to add sources to my notebook at any time so I can iteratively build up my knowledge base.
- As a user, I want to see all imported sources listed in the bottom-left panel so I know what content is available.
- As a user, I want to select one or more sources before chatting so the AI's answers are scoped to the content I choose.
- As a user, I want to ask the AI questions and receive answers that reference only my selected sources.
- As a user, I want to export the notebook's knowledge as a summary report, mind map, Word document, PowerPoint, or Excel file.

---

## 4. Functional Requirements

### 4.1 Home Page

**FR-HP-01 — Notebook Grid**
The home page shall display all existing notebooks in a responsive card grid. Each card shall show at minimum: notebook title, date last modified, and source count.

**FR-HP-02 — Create New Notebook Card**
A "Create New Notebook" card shall always appear as the first item in the grid. Clicking it navigates the user to the Notebook Creation page.

**FR-HP-03 — Empty State**
When no notebooks exist, the home page shall display only the "Create New Notebook" card together with a short onboarding message encouraging the user to create their first notebook.

**FR-HP-04 — Open Existing Notebook**
Clicking an existing notebook card shall navigate the user to the Notebook Detail page for that notebook.

---

### 4.2 Notebook Creation Page

**FR-NC-01 — Notebook Title**
On creation, the user shall provide a notebook title. The title shall appear in the most-left area of the page header and shall be editable in-line at any time.

**FR-NC-02 — Add Source Button**
An "Add Source" button shall be present in the top-left area of the content region. Clicking it shall open a source-import flow (see Section 4.4).

**FR-NC-03 — Source List Panel**
A panel in the bottom-left shall list all sources imported into the notebook. Each source entry shall display: source type icon, source name/title, and an option to remove the source.

**FR-NC-04 — Chatbot Panel**
A chatbot interface shall occupy the centre of the page. Prior to any sources being added, the chatbot shall display a prompt encouraging the user to add sources first.

**FR-NC-05 — Tools Panel**
A tools panel shall occupy the right side of the page and shall contain export actions (see Section 4.5).

---

### 4.3 Notebook Detail Page

The Notebook Detail page shall share the same layout as the Notebook Creation page (Section 4.2). All functional requirements FR-NC-01 through FR-NC-05 apply to the Detail page.

**FR-ND-01 — Source Selection for Chat**
The user shall be able to select one or more sources from the source list. Only selected sources shall be used as context for chatbot responses. All sources shall be selected by default when the detail page is first opened.

**FR-ND-02 — Chatbot Grounding**
The chatbot shall answer questions using only the content of the currently selected sources. If a question cannot be answered from the selected sources, the chatbot shall inform the user that no relevant information was found in the selected sources and shall not speculate beyond the provided content.

**FR-ND-03 — AI Integration**
The chatbot shall integrate with the MiniMax 2.7 API (Anthropic-compatible endpoint). All API calls shall be made server-side to protect credentials.

**FR-ND-04 — Chat History**
Chat history shall be persisted within the notebook session and shall be visible in the chatbot panel when the user returns to the notebook.

---

### 4.4 Source Import

**FR-SI-01 — Supported Source Types**

| Source Type | Details |
|---|---|
| Web Page (URL) | User provides a URL; the application fetches and indexes the page content. |
| Plain Text (.txt) | User uploads a .txt file. |
| Markdown (.md) | User uploads a .md file. |
| Word Document (.docx / .doc) | User uploads a Word document. |

**FR-SI-02 — Import Flow**
Clicking "Add Source" shall open a modal or side-drawer allowing the user to select a source type and then provide the URL or upload the file. The user shall receive visual feedback while the source is being processed and indexed.

**FR-SI-03 — Processing States**
Each source in the source list shall display one of the following states: Processing, Ready, or Failed (with an option to retry).

**FR-SI-04 — Multiple Sources**
A notebook shall support importing multiple sources. There is no hard upper limit defined for this release; performance targets are defined in Section 6.

**FR-SI-05 — Source Removal**
The user shall be able to remove any source from the notebook. Removal shall also delete the associated indexed content from the notebook's context.

---

### 4.5 Export Tools

The right-side tools panel shall provide the following export actions. Each action shall generate the output based on the content of all sources in the notebook (not limited to the chatbot's selected sources unless the tool specifies otherwise).

| Tool | Output | Description |
|---|---|---|
| Export Summary Report | PDF | AI-generated summary of all notebook sources. |
| Export Mind Map | Image or interactive format | Visual mind map of key topics and relationships extracted from sources. |
| Export to Word | .docx | Full content or summary exported as a Word document. |
| Export to PowerPoint | .pptx | Key points structured as a slide deck. |
| Export to Excel | .xlsx | Structured data or tables extracted from sources. |

**FR-ET-01** — Each export action shall show a progress indicator while the file is being generated.

**FR-ET-02** — Upon completion, the user shall be prompted to download the generated file.

---

## 5. UI & Visual Design Requirements

### 5.1 Layout — Home Page

- Full-width page with a shadow-grey background (`#F0F0F0` or equivalent).
- Notebook cards rendered on a white card surface with subtle drop shadow.
- Cards arranged in a responsive grid (e.g., 4 columns on desktop, 2 on tablet, 1 on mobile).
- "Create New Notebook" card shall be visually distinct (e.g., dashed border, plus icon).

### 5.2 Layout — Creation / Detail Page

The page shall be divided into the following regions:

| Region | Position | Content |
|---|---|---|
| Header / Title Bar | Top, full width | Notebook title (far left), global actions |
| Left Panel — Top | Top-left | "Add Source" button |
| Left Panel — Bottom | Bottom-left | Imported source list |
| Centre Panel | Middle | Chatbot interface |
| Right Panel | Right | Export tools |

### 5.3 Visual Style

- Page background: shadow grey.
- All content panels: white card style with rounded corners and soft drop shadow.
- Typography: clean sans-serif, high readability.
- Source type icons shall visually distinguish each source type (URL, TXT, MD, DOCX).
- The application name "H-NoteBook" shall appear in the global navigation or header.

### 5.4 Responsiveness

- The home page grid shall adapt to screen width.
- On smaller screens, the Detail page panels shall collapse into a tabbed or drawer navigation to remain usable.

---

## 6. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | Source indexing for a single document up to 50 pages shall complete within 30 seconds. |
| Performance | Chatbot first-token response shall begin within 3 seconds of query submission under normal load. |
| Reliability | The application shall target 99.5% uptime, excluding scheduled maintenance. |
| Security | API keys for MiniMax and any other third-party services shall never be exposed to the client. |
| Security | User notebooks and source content shall be isolated per user account. |
| Accessibility | The UI shall meet WCAG 2.1 Level AA guidelines. |
| Browser Support | The application shall support the latest two major versions of Chrome, Firefox, Safari, and Edge. |

---

## 7. Out of Scope for v1.0

- Audio and video source import.
- Real-time multi-user collaboration.
- Native mobile applications.
- Source versioning or change tracking.
- Notebook sharing or publishing.
- Custom AI model selection by the end user.

---

## 8. Open Questions

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | What is the maximum file size permitted for document uploads? | 10 MB.
| 2 | Should chat history persist indefinitely or have a retention policy? | yes, chat history will be persist in the database.
| 3 | Are there internationalisation (i18n) requirements for v1.0? | No, it uses English by default. 
| 4 | What user authentication mechanism will be used (SSO, email/password, etc.)? | Simple username password first(with harded value, no register)
| 5 | Should the mind map export be a static image or an interactive file format? | interactive file format

---

## 9. Success Metrics

| Metric | Target |
|---|---|
| Notebook creation rate | ≥ 3 notebooks created per active user per month |
| Source import success rate | ≥ 95% of import attempts succeed |
| Chatbot satisfaction (thumbs up/down) | ≥ 80% positive rating |
| Export feature adoption | ≥ 30% of active notebooks use at least one export tool per month |

---

## 10. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-03-23 | Product Management | Initial draft |
