/**
 * Multibliz POS - Advanced Table Features Library
 * Handles sortable columns, column visibility, inline editing, and bulk operations
 */

// ==================== SORTABLE COLUMNS ====================

class TableSorter {
    constructor(tableSelector, storageKey) {
        this.table = document.querySelector(tableSelector);
        this.storageKey = storageKey || 'table_sort_' + tableSelector;
        this.currentSort = this.loadSortState();
        this.init();
    }

    init() {
        if (!this.table) return;
        
        const headers = this.table.querySelectorAll('thead th[data-sortable="true"]');
        headers.forEach(th => {
            th.style.cursor = 'pointer';
            th.addEventListener('click', (e) => this.handleSort(e));
            this.addSortIndicator(th);
        });

        // Apply saved sort on page load
        if (this.currentSort) {
            this.applySort(this.currentSort.column, this.currentSort.direction);
        }
    }

    handleSort(e) {
        const th = e.target.closest('th[data-sortable="true"]');
        if (!th) return;

        const column = th.dataset.column;
        const currentDirection = th.dataset.direction || 'asc';
        const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';

        this.applySort(column, newDirection);
        this.saveSortState(column, newDirection);
    }

    applySort(column, direction) {
        const tbody = this.table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            const aCell = a.querySelector(`td[data-column="${column}"]`);
            const bCell = b.querySelector(`td[data-column="${column}"]`);

            if (!aCell || !bCell) return 0;

            let aValue = aCell.textContent.trim();
            let bValue = bCell.textContent.trim();

            // Try to parse as number
            const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
            const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));

            let comparison = 0;
            if (!isNaN(aNum) && !isNaN(bNum)) {
                comparison = aNum - bNum;
            } else {
                comparison = aValue.localeCompare(bValue);
            }

            return direction === 'asc' ? comparison : -comparison;
        });

        rows.forEach(row => tbody.appendChild(row));

        // Update visual indicators
        this.updateSortIndicators(column, direction);
    }

    updateSortIndicators(column, direction) {
        const headers = this.table.querySelectorAll('thead th[data-sortable="true"]');
        headers.forEach(th => {
            th.dataset.direction = '';
            th.classList.remove('sort-asc', 'sort-desc');
        });

        const activeHeader = this.table.querySelector(`thead th[data-column="${column}"]`);
        if (activeHeader) {
            activeHeader.dataset.direction = direction;
            activeHeader.classList.add(`sort-${direction}`);
        }
    }

    addSortIndicator(th) {
        const column = th.dataset.column;
        const indicator = document.createElement('span');
        indicator.className = 'sort-indicator';
        indicator.innerHTML = ' <i class="fas fa-arrows-up-down"></i>';
        th.appendChild(indicator);
    }

    saveSortState(column, direction) {
        localStorage.setItem(this.storageKey, JSON.stringify({ column, direction }));
        this.currentSort = { column, direction };
    }

    loadSortState() {
        const saved = localStorage.getItem(this.storageKey);
        return saved ? JSON.parse(saved) : null;
    }
}

// ==================== COLUMN VISIBILITY ====================

class ColumnToggle {
    constructor(tableSelector, storageKey) {
        this.table = document.querySelector(tableSelector);
        this.storageKey = storageKey || 'table_columns_' + tableSelector;
        this.columnState = this.loadColumnState();
        this.init();
    }

    init() {
        if (!this.table) return;

        // Get all column headers
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((th, index) => {
            const colName = th.dataset.column || th.textContent.trim();
            if (!this.columnState[colName]) {
                this.columnState[colName] = true;
            }
        });

        this.createToggleButton();
        this.applyColumnState();
    }

    createToggleButton() {
        const container = this.table.closest('.table-responsive') || this.table.parentElement;
        const existingBtn = container.querySelector('.column-toggle-btn');
        if (existingBtn) return;

        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-outline-secondary column-toggle-btn';
        btn.innerHTML = '<i class="fas fa-columns me-2"></i>Columns';
        btn.addEventListener('click', () => this.showToggleMenu());

        container.insertBefore(btn, container.firstChild);
    }

    showToggleMenu() {
        const headers = this.table.querySelectorAll('thead th');
        let menuHTML = '<div class="column-toggle-menu">';
        
        headers.forEach((th) => {
            const colName = th.dataset.column || th.textContent.trim();
            const isVisible = this.columnState[colName] !== false;
            
            menuHTML += `
                <label class="column-toggle-label">
                    <input type="checkbox" class="column-toggle-checkbox" 
                           data-column="${colName}" ${isVisible ? 'checked' : ''}>
                    <span>${colName}</span>
                </label>
            `;
        });

        menuHTML += '</div>';

        // Remove existing menu
        const existingMenu = document.querySelector('.column-toggle-menu');
        if (existingMenu) existingMenu.remove();

        // Create and show new menu
        const menu = document.createElement('div');
        menu.innerHTML = menuHTML;
        menu.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            border-radius: 0.5rem;
            padding: 1rem;
            min-width: 200px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
        `;

        document.body.appendChild(menu);

        const toggleBtn = document.querySelector('.column-toggle-btn');
        const rect = toggleBtn.getBoundingClientRect();
        menu.style.top = (rect.bottom + 5) + 'px';
        menu.style.left = rect.left + 'px';

        // Handle checkbox changes
        menu.querySelectorAll('.column-toggle-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.toggleColumn(e.target.dataset.column, e.target.checked);
            });
        });

        // Close menu on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.column-toggle-menu') && !e.target.closest('.column-toggle-btn')) {
                menu.remove();
            }
        }, { once: true });
    }

    toggleColumn(colName, isVisible) {
        this.columnState[colName] = isVisible;
        this.saveColumnState();
        this.applyColumnState();
    }

    applyColumnState() {
        const headers = this.table.querySelectorAll('thead th');
        const rows = this.table.querySelectorAll('tbody tr');

        headers.forEach((th, index) => {
            const colName = th.dataset.column || th.textContent.trim();
            const isVisible = this.columnState[colName] !== false;
            th.style.display = isVisible ? '' : 'none';
        });

        rows.forEach((row) => {
            const cells = row.querySelectorAll('td');
            cells.forEach((cell, index) => {
                const colName = headers[index]?.dataset.column || headers[index]?.textContent.trim();
                const isVisible = this.columnState[colName] !== false;
                cell.style.display = isVisible ? '' : 'none';
            });
        });
    }

    saveColumnState() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.columnState));
    }

    loadColumnState() {
        const saved = localStorage.getItem(this.storageKey);
        return saved ? JSON.parse(saved) : {};
    }
}

// ==================== BULK SELECT & ACTIONS ====================

class BulkActions {
    constructor(tableSelector, actions = []) {
        this.table = document.querySelector(tableSelector);
        this.actions = actions;
        this.selectedRows = new Set();
        this.init();
    }

    init() {
        if (!this.table) return;
        this.addCheckboxes();
        this.createActionBar();
        this.attachEventListeners();
    }

    addCheckboxes() {
        // Add checkbox to header
        const thead = this.table.querySelector('thead');
        const headerRow = thead.querySelector('tr');
        const headerCell = document.createElement('th');
        headerCell.innerHTML = '<input type="checkbox" class="bulk-select-all">';
        headerCell.style.width = '40px';
        headerRow.insertBefore(headerCell, headerRow.firstChild);

        // Add checkboxes to body rows
        const tbody = this.table.querySelector('tbody');
        tbody.querySelectorAll('tr').forEach((row, index) => {
            const cell = document.createElement('td');
            cell.innerHTML = `<input type="checkbox" class="bulk-select-row" data-row-id="${index}">`;
            cell.style.width = '40px';
            row.insertBefore(cell, row.firstChild);
        });
    }

    attachEventListeners() {
        const selectAll = this.table.querySelector('.bulk-select-all');
        selectAll?.addEventListener('change', (e) => this.selectAllRows(e.target.checked));

        this.table.querySelectorAll('.bulk-select-row').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => this.toggleRowSelection(e));
        });
    }

    selectAllRows(checked) {
        this.table.querySelectorAll('.bulk-select-row').forEach(checkbox => {
            checkbox.checked = checked;
            const rowId = checkbox.dataset.rowId;
            if (checked) {
                this.selectedRows.add(rowId);
            } else {
                this.selectedRows.delete(rowId);
            }
        });
        this.updateActionBar();
    }

    toggleRowSelection(e) {
        const rowId = e.target.dataset.rowId;
        if (e.target.checked) {
            this.selectedRows.add(rowId);
        } else {
            this.selectedRows.delete(rowId);
        }
        this.updateActionBar();
    }

    createActionBar() {
        const container = this.table.closest('.table-responsive') || this.table.parentElement;
        const actionBar = document.createElement('div');
        actionBar.className = 'bulk-action-bar';
        actionBar.style.display = 'none';
        actionBar.innerHTML = `
            <div class="d-flex align-items-center gap-3 p-3" style="background: #f3f4f6; border-radius: 0.5rem;">
                <span class="text-muted" id="bulk-count">0 selected</span>
                <div class="flex-grow-1"></div>
                <select class="form-select form-select-sm" id="bulk-action-select" style="max-width: 200px;">
                    <option value="">Select action...</option>
                    ${this.actions.map(a => `<option value="${a.id}">${a.label}</option>`).join('')}
                </select>
                <button class="btn btn-sm btn-primary" id="bulk-action-btn">Apply</button>
                <button class="btn btn-sm btn-outline-secondary" id="bulk-clear-btn">Clear</button>
            </div>
        `;
        container.insertBefore(actionBar, container.firstChild);

        document.getElementById('bulk-action-btn')?.addEventListener('click', () => this.executeBulkAction());
        document.getElementById('bulk-clear-btn')?.addEventListener('click', () => this.clearSelection());
    }

    updateActionBar() {
        const actionBar = document.querySelector('.bulk-action-bar');
        if (!actionBar) return;

        if (this.selectedRows.size > 0) {
            actionBar.style.display = 'block';
            document.getElementById('bulk-count').textContent = 
                `${this.selectedRows.size} selected`;
        } else {
            actionBar.style.display = 'none';
        }
    }

    clearSelection() {
        this.selectedRows.clear();
        this.table.querySelectorAll('.bulk-select-row, .bulk-select-all').forEach(cb => cb.checked = false);
        this.updateActionBar();
    }

    executeBulkAction() {
        const actionId = document.getElementById('bulk-action-select').value;
        if (!actionId) {
            alert('Please select an action');
            return;
        }

        const action = this.actions.find(a => a.id === actionId);
        if (action && action.callback) {
            action.callback(Array.from(this.selectedRows), this);
        }
    }

    getSelectedData() {
        const data = [];
        this.selectedRows.forEach(rowId => {
            const row = this.table.querySelector(`tbody tr:nth-child(${parseInt(rowId) + 1})`);
            if (row) {
                data.push({
                    rowId,
                    row,
                    data: row.dataset
                });
            }
        });
        return data;
    }
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tables with advanced features
    document.querySelectorAll('table[data-sortable="true"]').forEach(table => {
        const selector = '.' + table.className.split(' ')[0];
        new TableSorter(selector, 'sort_' + table.id);
    });

    document.querySelectorAll('table[data-toggleable="true"]').forEach(table => {
        const selector = '.' + table.className.split(' ')[0];
        new ColumnToggle(selector, 'cols_' + table.id);
    });

    document.querySelectorAll('table[data-bulkable="true"]').forEach(table => {
        const selector = '.' + table.className.split(' ')[0];
        const actions = JSON.parse(table.dataset.actions || '[]');
        new BulkActions(selector, actions);
    });
});

// Export for use in other contexts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TableSorter, ColumnToggle, BulkActions };
}
