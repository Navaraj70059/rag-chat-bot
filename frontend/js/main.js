
    const BACKEND_URL = 'http://127.0.0.1:8000';
    let selectedFile = null;
    let messageHistory = [];

    // ── FILE SELECTION ──
    $('#pdf-file').on('change', function () {
        selectedFile = this.files[0];
        if (selectedFile) {
        $('#file-name').text('📎 ' + selectedFile.name).show();
        }
    });

    // Drag & Drop
    const dropZone = $('#drop-zone');
    dropZone.on('dragover', function (e) {
        e.preventDefault();
        $(this).addClass('drag-over');
    });
    dropZone.on('dragleave', function () {
        $(this).removeClass('drag-over');
    });
    dropZone.on('drop', function (e) {
        e.preventDefault();
        $(this).removeClass('drag-over');
        const dt = e.originalEvent.dataTransfer;
        if (dt.files.length) {
        selectedFile = dt.files[0];
        $('#file-name').text('📎 ' + selectedFile.name).show();
        }
    });

    // ── PROCESS DOCUMENT ──
    $('#process-btn').on('click', function () {
        if (!selectedFile) {
        showUploadStatus('Please select a PDF file first.', 'error');
        return;
        }

        setProcessLoading(true);
        hideUploadStatus();

        const formData = new FormData();
        formData.append('file', selectedFile);

        $.ajax({
        url: BACKEND_URL + '/upload',
        method: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function (data) {
            setProcessLoading(false);
            showUploadStatus('✓ Document indexed successfully!', 'success');
            addDocToList(selectedFile.name);
            selectedFile = null;
            $('#file-name').hide();
            $('#pdf-file').val('');
        },
        error: function (xhr) {
            setProcessLoading(false);
            const msg = xhr.status === 0
            ? 'Cannot connect. Is FastAPI running on port 8000?'
            : 'Backend error: ' + xhr.status;
            showUploadStatus('✗ ' + msg, 'error');
        }
        });
    });

    function setProcessLoading(loading) {
        if (loading) {
        $('#process-btn').addClass('loading');
        $('#process-spinner').show();
        $('#process-label').text('Processing…');
        } else {
        $('#process-btn').removeClass('loading');
        $('#process-spinner').hide();
        $('#process-label').text('⚡ Process Document');
        }
    }

    function showUploadStatus(msg, type) {
        $('#upload-status').removeClass('success error info').addClass(type).text(msg).show();
    }

    function hideUploadStatus() {
        $('#upload-status').hide();
    }

    function addDocToList(name) {
        const $list = $('#docs-list');
        $list.find('.no-docs').remove();
        $list.append(`
        <div class="doc-item">
            <div class="doc-icon">🤖</div>
            <div class="doc-name">${escapeHtml(name)}</div>
            <div class="doc-badge">indexed</div>
        </div>
        `);
    }

    // ── CHAT ──
    function escapeHtml(text) {
        return $('<div>').text(text).html();
    }

    function getTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function appendMessage(role, content) {
        $('#welcome').hide();

        const isUser = role === 'user';
        const avatar = isUser ? '👤' : '🤖';
        const label = isUser ? 'You' : 'Assistant';

        const $msg = $(`
        <div class="msg ${isUser ? 'user' : 'ai'}">
            <div class="msg-avatar">${avatar}</div>
            <div class="msg-body">
            <div class="msg-meta">${label} · ${getTime()}</div>
            <div class="msg-bubble">${escapeHtml(content)}</div>
            </div>
        </div>
        `);

        $('#messages').append($msg);
        scrollToBottom();
        return $msg;
    }

    function showTyping() {
        const $typing = $(`
        <div class="msg ai" id="typing-msg">
            <div class="msg-avatar">🤖</div>
            <div class="msg-body">
            <div class="msg-meta">Assistant · thinking</div>
            <div class="msg-bubble">
                <div class="typing-indicator">
                <span></span><span></span><span></span>
                </div>
            </div>
            </div>
        </div>
        `);
        $('#messages').append($typing);
        scrollToBottom();
    }

    function hideTyping() {
        $('#typing-msg').remove();
    }

    function scrollToBottom() {
        const $m = $('#messages');
        $m.animate({ scrollTop: $m[0].scrollHeight }, 200);
    }

    function sendMessage(query) {
        if (!query.trim()) return;

        appendMessage('user', query);
        messageHistory.push({ role: 'user', content: query });

        $('#user-input').val('').css('height', 'auto');
        $('#send-btn').prop('disabled', true);
        showTyping();

        $.ajax({
        url: BACKEND_URL + '/ask?session_id=default_user',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ query: query }),
        success: function (data) {
            hideTyping();
            const answer = data.answer || 'No answer returned.';
            appendMessage('ai', answer);
            messageHistory.push({ role: 'assistant', content: answer });
            $('#send-btn').prop('disabled', false);
        },
        error: function (xhr) {
            hideTyping();
            const msg = xhr.status === 0
            ? 'Cannot reach the backend. Make sure FastAPI is running on port 8000.'
            : 'Error ' + xhr.status + ': ' + (xhr.responseJSON?.detail || 'Unknown error');
            appendMessage('ai', '⚠ ' + msg);
            $('#send-btn').prop('disabled', false);
        }
        });
    }

    // Send button
    $('#send-btn').on('click', function () {
        sendMessage($('#user-input').val());
    });

    // Enter key
    $('#user-input').on('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage($(this).val());
        }
    });

    // Auto-resize textarea
    $('#user-input').on('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 140) + 'px';
    });

    // Hint chips
    $(document).on('click', '.hint-chip', function () {
        const q = $(this).data('q');
        $('#user-input').val(q);
        sendMessage(q);
    });
