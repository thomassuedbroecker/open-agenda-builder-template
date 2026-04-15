// Client-side JavaScript for agenda management

// Utility Functions
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

function handleError(error) {
    console.error('Error:', error);
    showNotification(error.message || 'An error occurred', 'error');
}

// API Functions
async function addSession(sessionId) {
    try {
        const response = await fetch(`/api/agenda/add?session_id=${encodeURIComponent(sessionId)}`, {
            method: 'POST',
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to add session');
        }
        
        showNotification('✅ Session added to your agenda', 'success');
        await updateSelectedCount();
        highlightSession(sessionId, true);
        
    } catch (error) {
        handleError(error);
    }
}

async function removeSession(sessionId) {
    try {
        const response = await fetch(`/api/agenda/remove/${encodeURIComponent(sessionId)}`, {
            method: 'DELETE',
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to remove session');
        }
        
        showNotification('🗑️ Session removed from your agenda', 'success');
        
        // Remove from DOM if on my-agenda page
        const agendaItem = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (agendaItem && agendaItem.classList.contains('agenda-item')) {
            agendaItem.remove();
            
            // Check if agenda is now empty
            const remainingItems = document.querySelectorAll('.agenda-item');
            if (remainingItems.length === 0) {
                window.location.reload();
            }
        } else {
            highlightSession(sessionId, false);
        }
        
        await updateSelectedCount();
        
    } catch (error) {
        handleError(error);
    }
}

async function updateSelectedCount() {
    try {
        const response = await fetch('/api/agenda/sessions');
        const sessions = await response.json();
        
        const countElement = document.getElementById('selected-count');
        if (countElement) {
            countElement.textContent = `✅ ${sessions.length} selected`;
        }
        
        return sessions;
        
    } catch (error) {
        console.error('Error updating count:', error);
        return [];
    }
}

async function highlightSelectedSessions() {
    try {
        const sessions = await updateSelectedCount();
        const sessionIds = sessions.map(s => s.id);
        
        sessionIds.forEach(id => highlightSession(id, true));
        
    } catch (error) {
        console.error('Error highlighting sessions:', error);
    }
}

function highlightSession(sessionId, selected) {
    const card = document.querySelector(`[data-session-id="${sessionId}"]`);
    if (!card) return;
    
    if (selected) {
        card.classList.add('selected');
        const btn = card.querySelector('.add-session-btn');
        if (btn) {
            btn.textContent = '✅ Added';
            btn.disabled = true;
        }
    } else {
        card.classList.remove('selected');
        const btn = card.querySelector('.add-session-btn');
        if (btn) {
            btn.textContent = '➕ Add to My Agenda';
            btn.disabled = false;
        }
    }
}

// Export Functions
async function exportJSON() {
    try {
        const response = await fetch('/api/agenda/export/json');
        
        if (!response.ok) {
            throw new Error('Failed to export agenda');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `agenda_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('📥 Agenda exported as JSON', 'success');
        
    } catch (error) {
        handleError(error);
    }
}

async function exportICS() {
    try {
        const response = await fetch('/api/agenda/export/ics');
        
        if (!response.ok) {
            throw new Error('Failed to export calendar');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `agenda_${new Date().toISOString().split('T')[0]}.ics`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('📅 Calendar exported successfully', 'success');
        
    } catch (error) {
        handleError(error);
    }
}

// Import Functions
function showImportDialog() {
    const dialog = document.getElementById('import-dialog');
    if (dialog) {
        dialog.style.display = 'flex';
    }
}

function closeImportDialog() {
    const dialog = document.getElementById('import-dialog');
    if (dialog) {
        dialog.style.display = 'none';
    }
    
    const fileInput = document.getElementById('import-file');
    if (fileInput) {
        fileInput.value = '';
    }
}

async function importAgenda() {
    const fileInput = document.getElementById('import-file');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        showNotification('Please select a file to import', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/agenda/import', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to import agenda');
        }
        
        showNotification(`✅ Imported ${data.session_count} sessions`, 'success');
        closeImportDialog();
        
        // Reload page to show imported sessions
        setTimeout(() => {
            window.location.reload();
        }, 1000);
        
    } catch (error) {
        handleError(error);
    }
}

// Clear Agenda
async function clearAgenda() {
    if (!confirm('Are you sure you want to clear all sessions from your agenda?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/agenda/clear', {
            method: 'DELETE',
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to clear agenda');
        }
        
        showNotification('🗑️ Agenda cleared', 'success');
        
        // Reload page
        setTimeout(() => {
            window.location.reload();
        }, 1000);
        
    } catch (error) {
        handleError(error);
    }
}

// Navigation
function viewMyAgenda() {
    window.location.href = '/my-agenda';
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    const dialog = document.getElementById('import-dialog');
    if (dialog && e.target === dialog) {
        closeImportDialog();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeImportDialog();
    }
});
