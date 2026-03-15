console.log("Loaded chatview.js file")
const vscode = acquireVsCodeApi();
const chat = document.getElementById("chat");
const input = document.getElementById("input");
const commandMenu = document.getElementById("command-menu");
let selectedCommandIndex = -1;

const commands = [
  { name: "/new", description: "Start a new conversation" },
  { name: "/clear", description: "Clear chat history" },
  {
    name: "/generate-code",
    description: "Generate API/client code using template",
  },
];

const IVP_PRODUCTS = [
  "IVP Polaris",
  "IVP RAD Dev",
  "IVP Price Master",
  "IVP PnL Monitor 2.0",
  "IVP Recon 4.9",
  "IVP Security Master v5.3",
  "IVP Sec Master Excel Add-in",
  "IVP Recon 6.5",
  "IVP Security Master 6.5",
  "IVP Security Master v6.5",
  "IVP Reference Master v2.0",
  "IVP Reference Master v3.0",
  "IVP Solutions Documentation",
  "IVP EDM DEV",
  "IVP Security Master 8.0",
  "IVP Security Master v8.0",
  "IVP Security Master v8.5",
  "IVP Cash Master v6.0",
  "IVP OMS v3.0",
  "IVP Treasury v5.0",
  "IVP Polaris User Manual v10.0",
  "IVP Polaris User Manual v12.0",
  "IVP Risk Service",
  "IVP SRM Technical Specs",
  "IVP SRM v15.0",
  "IVP Raptor v11.2",
  "IVP Raptor v11.3",
  "IVP EDM v2.4",
  "IVP EDM v3.0",
  "IVP EDM v3.5",
  "IVP EDM v3.5.1",
  "IVP EDM v4.0",
  "IVP EDM v4.5",
  "IVP EDM v15.0",
  "IVP Price Master Excel Add-in v5.0",
  "IVP Price Master Excel Add-in v5.0.17",
  "IVP Expense Manager v1007",
  "IVP ORKA v15.0",
  "IVP Polaris v15.0",
  "IVP Polaris Excel Add-in v12.0",
  "IVP Cash Master v7.0",
  "IVP Reference Master v3.2",
];

// Configure marked.js options
marked.setOptions({
  breaks: true,
  gfm: true,
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (err) {}
    }
    return hljs.highlightAuto(code).value;
  },
});

// Request chat history when webview loads
vscode.postMessage({ type: "requestHistory" });

// Show/hide command menu based on input
input.addEventListener("input", function () {
  const value = input.value;
  if (value === "/" || value.startsWith("/")) {
    showCommandMenu();
    filterCommands(value);
  } else {
    hideCommandMenu();
  }
});

// Handle clicks outside to close menu
document.addEventListener("click", function (e) {
  if (!input.contains(e.target) && !commandMenu.contains(e.target)) {
    hideCommandMenu();
  }
});

// Handle command item clicks
document.querySelectorAll(".command-item").forEach((item) => {
  item.addEventListener("click", function () {
    const command = this.getAttribute("data-command");
    input.value = command;
    hideCommandMenu();
    input.focus();
  });
});

function showCommandMenu() {
  commandMenu.classList.add("visible");
  selectedCommandIndex = -1;
  updateSelectedCommand();
}

function hideCommandMenu() {
  commandMenu.classList.remove("visible");
  selectedCommandIndex = -1;
}

function filterCommands(value) {
  const items = commandMenu.querySelectorAll(".command-item");
  let visibleCount = 0;

  items.forEach((item) => {
    const command = item.getAttribute("data-command");
    if (command.startsWith(value.toLowerCase())) {
      item.style.display = "flex";
      visibleCount++;
    } else {
      item.style.display = "none";
    }
  });

  // Hide menu if no matches
  if (visibleCount === 0) {
    hideCommandMenu();
  }
}

function updateSelectedCommand() {
  const items = Array.from(
    commandMenu.querySelectorAll(".command-item"),
  ).filter((item) => item.style.display !== "none");

  items.forEach((item, index) => {
    if (index === selectedCommandIndex) {
      item.classList.add("selected");
    } else {
      item.classList.remove("selected");
    }
  });
}

function handleKeyDown(event) {
  const isMenuVisible = commandMenu.classList.contains("visible");

  if (isMenuVisible) {
    const visibleItems = Array.from(
      commandMenu.querySelectorAll(".command-item"),
    ).filter((item) => item.style.display !== "none");

    if (event.key === "ArrowDown") {
      event.preventDefault();
      selectedCommandIndex = Math.min(
        selectedCommandIndex + 1,
        visibleItems.length - 1,
      );
      updateSelectedCommand();
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      selectedCommandIndex = Math.max(selectedCommandIndex - 1, 0);
      updateSelectedCommand();
    } else if (event.key === "Enter") {
      if (
        selectedCommandIndex >= 0 &&
        selectedCommandIndex < visibleItems.length
      ) {
        event.preventDefault();
        const command =
          visibleItems[selectedCommandIndex].getAttribute("data-command");
        input.value = command;
        hideCommandMenu();
        return;
      }
      send();
    } else if (event.key === "Escape") {
      event.preventDefault();
      hideCommandMenu();
    }
  } else if (event.key === "Enter") {
    send();
  }
}

function addMessage(text, cls) {
  const div = document.createElement("div");
  div.className = "message " + cls;

  if (cls === "assistant") {
    const wrapper = document.createElement("div");
    wrapper.className = "assistant-message-wrapper";

    const contentDiv = document.createElement("div");
    contentDiv.className = "assistant-content";
    contentDiv.innerHTML = marked.parse(text);

    renderMermaid(contentDiv);

    /* TOOLBAR */

    const toolbar = document.createElement("div");
    toolbar.className = "message-toolbar";

    /* COPY BUTTON */

    const copyBtn = document.createElement("button");
    copyBtn.className = "toolbar-btn codicon codicon-copy";

    copyBtn.onclick = () => {
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.classList.remove("codicon-copy");
        copyBtn.classList.add("codicon-check");

        setTimeout(() => {
          copyBtn.classList.remove("codicon-check");
          copyBtn.classList.add("codicon-copy");
        }, 1500);
      });
    };

    /* THUMBS UP */

    const upBtn = document.createElement("button");
    upBtn.className = "toolbar-btn codicon codicon-thumbsup";

    upBtn.onclick = () => {
      vscode.postMessage({
        type: "feedback",
        value: "up",
        message: text,
      });
    };

    /* THUMBS DOWN */

    const downBtn = document.createElement("button");
    downBtn.className = "toolbar-btn codicon codicon-thumbsdown";

    downBtn.onclick = () => {
      vscode.postMessage({
        type: "feedback",
        value: "down",
        message: text,
      });
    };

    /* REGENERATE */

    const regenBtn = document.createElement("button");
    regenBtn.className = "toolbar-btn codicon codicon-refresh";

    regenBtn.onclick = () => {
      vscode.postMessage({
        type: "regenerate",
        message: text,
      });
    };

    toolbar.appendChild(copyBtn);
    toolbar.appendChild(upBtn);
    toolbar.appendChild(downBtn);
    toolbar.appendChild(regenBtn);

    /* CODE BLOCK COPY */

    contentDiv.querySelectorAll("pre code").forEach((block) => {
      const codeWrapper = document.createElement("div");
      codeWrapper.className = "code-block-wrapper";

      const codeCopyBtn = document.createElement("button");
      codeCopyBtn.className = "copy-button";
      codeCopyBtn.textContent = "Copy";

      codeCopyBtn.onclick = () => {
        const code = block.textContent;

        navigator.clipboard.writeText(code).then(() => {
          codeCopyBtn.textContent = "Copied!";
          codeCopyBtn.classList.add("copied");

          setTimeout(() => {
            codeCopyBtn.textContent = "Copy";
            codeCopyBtn.classList.remove("copied");
          }, 2000);
        });
      };

      const pre = block.parentElement;

      pre.parentElement.insertBefore(codeWrapper, pre);
      codeWrapper.appendChild(pre);
      codeWrapper.appendChild(codeCopyBtn);
    });

    wrapper.appendChild(contentDiv);
    wrapper.appendChild(toolbar);

    div.appendChild(wrapper);
  } else {
    div.textContent = text;
  }

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}
function sanitizeMermaid(source) {
  return (
    source
      // Replace unicode arrows
      .replace(/→/g, "->")
      .replace(/←/g, "<-")
      .replace(/⇒/g, "=>")

      // Replace smart quotes
      .replace(/[“”]/g, '"')
      .replace(/[‘’]/g, "'")

      // Normalize ellipsis
      .replace(/…/g, "...")

      // REMOVE ALL PARENTHESES
      .replace(/[()]/g, "")
  );
}
function renderMermaid(container) {
  const mermaidBlocks = container.querySelectorAll("pre code.language-mermaid");
  const mermaidNodes = [];

  mermaidBlocks.forEach((block) => {
    const parentPre = block.parentElement;
    const graphDefinition = block.textContent;

    const mermaidDiv = document.createElement("div");
    mermaidDiv.className = "mermaid";
    mermaidDiv.textContent = graphDefinition;

    parentPre.replaceWith(mermaidDiv);
    mermaidNodes.push(mermaidDiv);
  });

  if (mermaidNodes.length > 0) {
    try {
      // Sanitize Mermaid definitions before rendering
      mermaidNodes.forEach((node) => {
        node.textContent = sanitizeMermaid(node.textContent);
      });
      mermaid.run({ nodes: mermaidNodes });
    } catch (err) {
      console.error("Mermaid render failed:", err);
      // HARD FAIL: remove all Mermaid output
      mermaidNodes.forEach((div) => div.remove());
    }
  }
}

function send(templatePrompt = null) {
  let text = templatePrompt || input.value.trim();

  // Detect if template exists and Send button was used
  if (!templatePrompt) {
    const template = document.querySelector(".code-template");

    if (template) {
      const root = template.closest(".message");
      const generatedPrompt = buildPrompt(root);

      if (!generatedPrompt) {
        addMessage(
          "Please complete product and functionality fields before sending.",
          "system",
        );
        return;
      }

      text = generatedPrompt;

      // remove template after sending
      root.remove();
    }
  }

  if (!text) return;

  hideCommandMenu();

  // handle /clear and /new
  if (text.toLowerCase() === "/clear" || text.toLowerCase() === "/new") {
    vscode.postMessage({ type: "userMessage", text });
    input.value = "";
    return;
  }

  // handle /generate-code
  if (text.toLowerCase() === "/generate-code") {
    renderCodeTemplate();
    input.value = "";
    return;
  }

  // display message in chat
  addMessage(text, "user");

  // send to extension
  vscode.postMessage({
    type: "userMessage",
    text,
  });

  input.value = "";
}

function renderCodeTemplate() {
  const div = document.createElement("div");
  div.className = "message assistant";

  div.innerHTML = `
	<div class="code-template">

	<h3>Code Generation Template</h3>

	<div class="template-row">
	<label>Code Type</label>
	<select id="code-type">
	<option value="">Select Code Type</option>
	<option value="rest">REST Endpoint</option>
	<option value="csharp">C# Client</option>
	<option value="python">Python Client</option>
	<option value="javascript">JavaScript Client</option>
	</select>
	</div>

	<div id="products-container"></div>

	<button id="add-product">Add Product</button>

	<div class="template-actions">
	<button id="generate-code">Generate Code</button>
	</div>

	</div>
	`;

  chat.appendChild(div);
  initializeTemplateEvents(div);
}
function isEndpointValid(container) {
  const rows = container.querySelectorAll(".endpoint-row");

  if (rows.length === 0) return false;

  const last = rows[rows.length - 1]
    .querySelector(".endpoint-name")
    .value.trim();

  return last.length > 0;
}

function isProductValid(block) {
  const product = block.querySelector(".product-search").value.trim();

  const endpoints = block.querySelectorAll(".endpoint-name");

  if (!product) return false;

  for (const ep of endpoints) {
    if (ep.value.trim()) return true;
  }

  return false;
}

function createProductSelector() {
  const options = IVP_PRODUCTS.map(
    (p) => `<div class="product-option">${p}</div>`,
  ).join("");

  return `
	<div class="product-select-wrapper">

	<input class="product-search" placeholder="Search product..." />

	<div class="product-dropdown">
	${options}
	</div>

	</div>
	`;
}
function createEndpointRow() {
  return `
<div class="endpoint-row">

<input class="endpoint-name"
placeholder="Describe functionality (Create Trade, Get Portfolio Positions)">

<button class="delete-btn delete-endpoint">✕</button>

</div>
`;
}

function createProductBlock() {
  return `
<div class="product-block">

<div class="product-header">
<span>Product</span>
<button class="delete-btn delete-product">✕</button>
</div>

${createProductSelector()}

<div class="endpoints-container"></div>

<button class="add-endpoint template-add">Add Functionality</button>

</div>
`;
}

function initializeTemplateEvents(root) {
  const productsContainer = root.querySelector("#products-container");
  const addProductBtn = root.querySelector("#add-product");

  /* ADD PRODUCT */

  addProductBtn.onclick = () => {
    const blocks = productsContainer.querySelectorAll(".product-block");

    if (blocks.length) {
      const last = blocks[blocks.length - 1];

      if (!isProductValid(last)) {
        addMessage(
          "Finish selecting a product and at least one functionality before adding another.",
          "system",
        );

        return;
      }
    }

    const wrapper = document.createElement("div");
    wrapper.innerHTML = createProductBlock();

    const block = wrapper.firstElementChild;

    productsContainer.appendChild(block);

    initializeProductSearch(block);
    attachProductHandlers(block);
  };

  /* GENERATE CODE BUTTON */

  root.querySelector("#generate-code").onclick = () => {
    const prompt = buildPrompt(root);

    if (!prompt) {
      addMessage("Please complete product and functionality fields.", "system");

      return;
    }

    send(prompt);

    // remove template after sending
    root.remove();
  };
}

function attachProductHandlers(block) {
  const endpointsContainer = block.querySelector(".endpoints-container");

  /* ADD FUNCTIONALITY */

  block.querySelector(".add-endpoint").onclick = () => {
    if (
      !isEndpointValid(endpointsContainer) &&
      endpointsContainer.children.length
    ) {
      addMessage(
        "Fill the current functionality before adding another.",
        "system",
      );

      return;
    }

    const row = document.createElement("div");
    row.innerHTML = createEndpointRow();

    const el = row.firstElementChild;

    endpointsContainer.appendChild(el);

    /* delete functionality */

    el.querySelector(".delete-endpoint").onclick = () => {
      el.remove();
    };
  };

  /* delete product */

  block.querySelector(".delete-product").onclick = () => {
    block.remove();
  };
}
function buildPrompt(root) {
  const codeType = root.querySelector("#code-type").value;

  if (!codeType) return null;

  const blocks = root.querySelectorAll(".product-block");

  if (!blocks.length) return null;

  let productList = [];
  let sections = [];
  let index = 1;

  for (const block of blocks) {
    const product = block.querySelector(".product-search").value.trim();

    if (!product) continue;

    const endpoints = block.querySelectorAll(".endpoint-name");

    let funcs = [];

    endpoints.forEach((ep) => {
      const val = ep.value.trim();
      if (val) funcs.push(val);
    });

    if (!funcs.length) continue;

    productList.push(product);

    let section = `${index}. Use ${product} to create the following functionality:\n`;

    funcs.forEach((f) => {
      section += `- ${f}\n`;
    });

    sections.push(section);

    index++;
  }

  if (!sections.length) return null;

  const prompt = `Generate a code block for ${codeType} based on the following products ${productList.join(", ")}.

${sections.join("\n")}

Use ${codeType} for the implementation.

Follow industry best practices, clean architecture, proper authentication handling,
clear function naming, modular functions, and produce clean well-formatted code blocks.`;

  return prompt;
}

function initializeProductSearch(block) {
  const search = block.querySelector(".product-search");
  const dropdown = block.querySelector(".product-dropdown");
  const options = dropdown.querySelectorAll(".product-option");

  search.addEventListener("focus", () => {
    dropdown.classList.add("visible");
  });

  search.addEventListener("input", () => {
    const value = search.value.toLowerCase();

    options.forEach((opt) => {
      if (opt.textContent.toLowerCase().includes(value)) {
        opt.style.display = "block";
      } else {
        opt.style.display = "none";
      }
    });
  });

  options.forEach((opt) => {
    opt.onclick = () => {
      search.value = opt.textContent;
      dropdown.classList.remove("visible");
    };
  });
}
function collectTemplateData(root) {
  const codeType = root.querySelector("#code-type").value;
  if (!codeType) return { valid: false };

  const products = [];

  root.querySelectorAll(".product-block").forEach((productBlock) => {
    const productName = productBlock.querySelector(".product-search").value;

    if (!productName) return;

    const endpoints = [];

    productBlock.querySelectorAll(".endpoint-row").forEach((row) => {
      const name = row.querySelector(".endpoint-name").value;
      const url = row.querySelector(".endpoint-url").value;
      const auth = row.querySelector(".auth-type").value;

      if (name && url) {
        endpoints.push({ name, url, auth });
      }
    });

    if (endpoints.length > 0) {
      products.push({
        product: productName,
        endpoints,
      });
    }
  });

  if (products.length === 0) return { valid: false };

  return {
    valid: true,
    data: {
      codeType,
      products,
    },
  };
}

window.addEventListener("message", (event) => {
  const msg = event.data;

  if (msg.type === "assistant") {
    addMessage(msg.text, "assistant");
  } else if (msg.type === "loadHistory") {
    // Load chat history
    chat.innerHTML = "";
    msg.history.forEach((item) => {
      addMessage(item.text, item.type);
    });
  } else if (msg.type === "clearHistory") {
    // Clear chat history with optional system message
    chat.innerHTML = "";
    if (msg.message) {
      addMessage(msg.message, "system");
    } else {
      addMessage("Chat history cleared.", "system");
    }
  }
});

window.handleKeyDown = handleKeyDown;
window.send = send;

// Focus input on load
input.focus();
