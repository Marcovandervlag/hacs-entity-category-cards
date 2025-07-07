class HacsEntityCategoryCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this.attachShadow({mode: 'open'});
    this.render();
    this.loadEntities();
  }

  async loadEntities() {
    const resp = await fetch('/local/entities.json');
    this.entities = await resp.json();
    this.domains = [...new Set(this.entities.map(e => e['Entity ID'].split('.')[0]))];
    this.selectedDomain = this.domains[0];
    this.render();
  }

  render() {
    if (!this.shadowRoot) return;
    this.shadowRoot.innerHTML = `
      <style>
        .card { background: linear-gradient(135deg, #f8ffae 0%, #43c6ac 100%);
                border-radius: 1.5em; box-shadow: 0 4px 24px 0 rgba(0,0,0,0.18);
                padding: 1.5em; animation: fadeIn 0.7s; }
        select, table { font-size: 1em; margin: 1em 0; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); }
                            to { opacity: 1; transform: translateY(0); } }
      </style>
      <div class="card">
        <h2>Entities by Category</h2>
        <label>Select category:
          <select id="domain-select">
            ${(this.domains||[]).map(d => `<option value="${d}">${d}</option>`).join('')}
          </select>
        </label>
        <div id="entity-table"></div>
      </div>
    `;
    this.shadowRoot.querySelector('#domain-select')?.addEventListener('change', (e) => {
      this.selectedDomain = e.target.value;
      this.renderTable();
    });
    this.renderTable();
  }

  renderTable() {
    if (!this.entities || !this.selectedDomain) return;
    const filtered = this.entities.filter(e => e['Entity ID'].startsWith(this.selectedDomain + '.'));
    const table = `
      <table>
        <tr><th>Entity ID</th><th>Friendly Name</th></tr>
        ${filtered.map(e => `<tr><td>${e['Entity ID']}</td><td>${e['Friendly Name']||''}</td></tr>`).join('')}
      </table>
    `;
    this.shadowRoot.querySelector('#entity-table').innerHTML = table;
  }

  getCardSize() { return 4; }
}

customElements.define('hacs-entity-category-card', HacsEntityCategoryCard);
