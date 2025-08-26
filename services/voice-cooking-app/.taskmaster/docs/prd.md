# PRD: Recipe Import from TikTok & Pinterest

## 📌 Summary

Enable users to import recipes from TikTok and Pinterest. For TikTok, rely on the post description text to parse recipes. For Pinterest, use the “Visit Site” link to fetch the canonical recipe page, then parse recipes from that external site.

---

## 🎯 Goals

* Let users easily add recipes discovered on TikTok and Pinterest into the app.
* Provide a seamless “share/import” flow from social platforms to our structured recipe schema.
* Ensure imports are **compliant** (no scraping TikTok media; respect Pinterest’s outbound links).

---

## 👩‍🍳 User Stories

1. **As a user**, when I paste a TikTok URL, I want the app to extract the post description and parse any recipe content.
2. **As a user**, when I paste a Pinterest URL, I want the app to follow the “Visit Site” link and parse the recipe from the target site automatically.
3. **As a user**, if parsing fails, I want to manually edit or complete the recipe within the app.

---

## 🛠️ Technical Details

### TikTok Import

* **Input:** TikTok URL (e.g., `https://www.tiktok.com/@user/video/12345`).
* **Fetch:** Use TikTok’s official **oEmbed endpoint** for metadata (author, thumbnail, description).
* **Parse:** Run NLP on the `description` field for potential ingredient lines and step-like instructions.
* **Fallback:** If description has no recipe structure, show user “Low confidence import” with option to add manually.
* **Compliance:** Do **not** attempt to scrape or download TikTok video/audio directly.

### Pinterest Import

* **Input:** Pinterest URL (e.g., `https://www.pinterest.com/pin/12345`).
* **Fetch:** Use Pinterest’s HTML/metadata to extract the **“Visit Site”** canonical link.
* **Parse:** Send user to that target recipe page, fetch HTML, look for JSON-LD `@type: Recipe` or use site-specific scraper.
* **Fallback:** If no JSON-LD present, run heuristics (ingredient regex + instruction segmentation).
* **Compliance:** Only follow and parse the external target URL, not Pinterest’s own HTML content.

---

## 📂 Data Schema (Recipe Object)

```json
{
  "title": "string",
  "source": {
    "platform": "tiktok|pinterest",
    "url": "string",
    "author": "string"
  },
  "ingredients": [
    {"name": "string", "quantity": "string", "unit": "string"}
  ],
  "steps": ["string"],
  "images": ["url"],
  "confidence": 0.0
}
```

---

## ✅ Acceptance Criteria

**TikTok**

* Given a valid TikTok URL, app fetches description via oEmbed.
* App attempts to parse at least one ingredient or step.
* If parsing fails, user sees fallback UI to edit recipe manually.

**Pinterest**

* Given a valid Pinterest URL, app follows “Visit Site” link.
* App fetches external page HTML and checks for `@type: Recipe`.
* If JSON-LD exists, parse into recipe schema.
* If not, attempt regex-based fallback.
* If all fails, user sees manual-edit screen.

---

## 🔮 Future Enhancements

* TikTok: Add ASR/OCR pipeline when video files are available.
* Pinterest: Handle common food blogs with custom scrapers for more robust parsing.
* Unified share target flow (share TikTok/Pinterest links directly to app).
