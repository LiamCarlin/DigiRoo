# Making hashtags real, not decorative

The TikTok upload caption box is a rich-text editor, not a plain textarea. A hashtag only works if the editor converted your text into a **hashtag entity** — an internal object with its own styling. Text that merely starts with `#` is inert. It will publish, it will look almost right, and the video will never enter that hashtag's feed.

## What creates an entity vs. what doesn't

| Action | Result |
|---|---|
| Paste a caption that already contains `#fyp` | **Plain text.** Always. Pasting never triggers the parser. This is the single most common cause. |
| Type `#fyp` then press space | **Unreliable.** Sometimes converts, often doesn't, and behaves differently depending on whether the autocomplete panel was open. Do not rely on it. |
| Type `#`, wait for the panel, then click a suggestion | **Entity.** This is the only method to use. |
| Type `#`, wait for the panel, arrow to a suggestion, press Enter | **Entity.** Acceptable fallback if the click target is unstable. |
| Type `#fyp` then click elsewhere / tab away | **Plain text.** |

Corollary: **never paste the full caption.** Type the body, then add hashtags one at a time through the panel.

## The procedure

For each hashtag, in order:

1. Click at the end of the caption text to place the cursor. Type a single space first if the previous character isn't already whitespace — two entities jammed together will merge into one bad tag.
2. Type `#`. A dropdown panel appears below the caption box listing hashtags with view counts.
3. Type the tag name **slowly enough that the panel filters** — the panel is debounced. After typing, wait ~700ms and re-screenshot before acting; acting on a stale panel selects the wrong tag.
4. Find the exact match in the panel. It's usually first, but not always — a more popular near-match often outranks it. Match the string exactly.
5. **Click the exact match.** The panel closes and the hashtag appears in the caption in TikTok's accent color.
6. Confirm a space was inserted after it. If the cursor is still glued to the entity, type a space before the next hashtag.

If the exact tag you want doesn't appear in the panel at all, it's a brand-new tag with no posts. Type it fully and press space, then verify — if it stays plain text, drop it and pick an established tag instead. A brand-new hashtag delivers no distribution anyway.

## Verification — do this before scheduling every single post

**Visual check.** Screenshot the caption box. Real hashtags render in TikTok's accent color, clearly distinct from the body text. Plain-text hashtags are the same color as the rest of the caption. Scanning for "is that line a different color" catches nearly everything.

**DOM check.** Run this via `javascript_tool` for a definitive answer:

```js
(() => {
  const box = document.querySelector('[contenteditable="true"]');
  if (!box) return 'CAPTION BOX NOT FOUND';
  const text = box.innerText;
  const typed = (text.match(/#[\wÀ-ɏ]+/g) || []);
  // entities are rendered as styled child nodes, not bare text nodes
  const styled = [...box.querySelectorAll('span,a')]
    .map(n => n.innerText.trim())
    .filter(t => /^#[\wÀ-ɏ]+$/.test(t) && getComputedStyle(n).color !== getComputedStyle(box).color);
  return {
    typedHashtags: typed,
    liveEntities: styled,
    dead: typed.filter(t => !styled.includes(t))
  };
})()
```

If `dead` is non-empty, those hashtags are broken. Fix them before scheduling.

**Repair.** Select the dead hashtag with a click-drag or repeated shift+Left, delete it, and redo it through the panel. Do not try to "fix" it by adding a space or retyping the `#` in place — the editor keeps the text node it already committed.

## Related traps

- **@ mentions behave identically.** Same panel, same rule: select from the dropdown or the mention is dead text.
- **Hashtags in the middle of a sentence** work fine and count the same as ones at the end. Placement doesn't affect distribution — only entity status does.
- **Editing a caption after scheduling** re-opens the same editor with the same trap. Re-verify after any edit.
- **Caption length** is 2,200 characters, but only roughly the first 150 show before the "more" cut. Hashtags count toward the limit and push your hook out of view if the body runs long.
- **Emoji before a `#`** can swallow the trigger. Put a plain space between any emoji and a hashtag.
