(function () {
  'use strict';

  var BLOCK_TAGS = new Set(['P', 'LI', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
                            'BLOCKQUOTE', 'TD', 'TH', 'DT', 'DD', 'FIGURE',
                            'FIGCAPTION', 'SECTION', 'ASIDE']);

  /** Return the nearest block-level ancestor of el, stopping before .entry */
  function nearestBlock(el) {
    var node = el.parentNode;
    while (node && node !== document.body) {
      if (node.classList && node.classList.contains('entry')) break;
      if (BLOCK_TAGS.has(node.nodeName)) return node;
      node = node.parentNode;
    }
    return el.parentNode; // fallback
  }

  /**
   * Return the direct child of `block` that is an ancestor of (or is) `el`.
   * This is the inline node we insert the popover after, so it lands inside
   * the block right after the reference line rather than below the whole block.
   */
  function childInBlock(block, el) {
    var node = el;
    while (node && node.parentNode !== block) {
      node = node.parentNode;
    }
    return node;
  }

  /** Remove all id attributes from a subtree (prevents duplicate IDs) */
  function stripIds(root) {
    root.removeAttribute && root.removeAttribute('id');
    var children = root.querySelectorAll ? root.querySelectorAll('[id]') : [];
    for (var i = 0; i < children.length; i++) {
      children[i].removeAttribute('id');
    }
  }

  /** Close and remove all open popovers */
  function closeAll() {
    var open = document.querySelectorAll('.footnote-popover');
    for (var i = 0; i < open.length; i++) {
      open[i].parentNode && open[i].parentNode.removeChild(open[i]);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var refs = document.querySelectorAll('a.footnote[href^="#fn:"]');
    if (!refs.length) return;

    // Signal to CSS that JS is active → hide bottom footnotes list
    document.body.classList.add('js-footnotes');

    refs.forEach(function (ref) {
      ref.addEventListener('click', function (e) {
        e.preventDefault();

        var fnId     = ref.getAttribute('href').slice(1); // e.g. "fn:local-min"
        var popId    = 'popover-' + fnId;
        var existing = document.getElementById(popId);

        if (existing) {
          // Toggle off
          existing.parentNode && existing.parentNode.removeChild(existing);
          return;
        }

        // Close any other open popover first
        closeAll();

        // Locate the source footnote list item
        var source = document.getElementById(fnId);
        if (!source) return;

        // Deep-clone the content, then clean it up
        var content = source.cloneNode(true);
        stripIds(content);

        // Remove the ↩ back-link
        var backlinks = content.querySelectorAll('.reversefootnote');
        backlinks.forEach(function (bl) {
          bl.parentNode && bl.parentNode.removeChild(bl);
        });

        // Build the popover element
        var popover = document.createElement('div');
        popover.className = 'footnote-popover';
        popover.id = popId;
        popover.setAttribute('role', 'note');

        // Close button
        var btn = document.createElement('button');
        btn.className = 'footnote-popover-close';
        btn.setAttribute('aria-label', 'Close footnote');
        btn.textContent = '\u2715'; // ✕
        btn.addEventListener('click', function (ev) {
          ev.stopPropagation();
          popover.parentNode && popover.parentNode.removeChild(popover);
        });

        popover.appendChild(btn);

        // Move cloned children into popover
        while (content.firstChild) {
          popover.appendChild(content.firstChild);
        }

        // Insert inside the nearest block ancestor, right after the child node
        // that contains the <sup>. This places the popover below the specific
        // line where the reference appears, not below the whole paragraph.
        var sup    = ref.closest('sup') || ref.parentNode;
        var block  = nearestBlock(sup);
        var anchor = childInBlock(block, sup) || sup;

        // If the very next sibling is a text node starting with punctuation
        // (e.g. ", " or ". "), skip past that one character so the punctuation
        // stays attached to the preceding line rather than appearing after the box.
        var nextNode = anchor.nextSibling;
        if (nextNode && nextNode.nodeType === 3 && /^[,\.;:!?]/.test(nextNode.textContent)) {
          nextNode.splitText(1); // splits ", rest" into "," and " rest"
          anchor = nextNode;     // insert after the lone punctuation text node
        }

        block.insertBefore(popover, anchor.nextSibling);

        // Re-typeset any math that ended up in the popover
        if (window.MathJax && window.MathJax.typesetPromise) {
          window.MathJax.typesetPromise([popover]).catch(function () {});
        }
      });
    });

    // Close on outside click (but not on clicks inside a popover or on a ref link)
    document.addEventListener('click', function (e) {
      if (e.target.closest && (
            e.target.closest('.footnote-popover') ||
            e.target.closest('a.footnote')
          )) {
        return;
      }
      closeAll();
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeAll();
    });
  });
}());
