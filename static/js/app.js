// 全局變數
let currentEditingNoteId = null;
const API_BASE_URL = 'http://127.0.0.1:8000';

// 初始化 Marked.js 和 Material Components
document.addEventListener('DOMContentLoaded', () => {
    // 綁定檔案上傳相關事件
    initializeFileUpload();
    
    // 自定義渲染器，處理圖片路徑問題
    const renderer = new marked.Renderer();
    
    // 重寫圖片渲染方法
    renderer.image = function(href, title, text) {
        console.log("接收到的圖片參數:", { href, title, text });
        
        // 檢查參數類型，確保安全處理
        if (typeof href === 'object') {
            console.log("收到物件類型的 href:", href);
            // 如果是 marked.js 新版本傳遞的完整 token 物件
            if (href && href.href) {
                href = href.href;
            } else if (href && href.src) {
                href = href.src;
            } else if (href && href.url) {
                href = href.url;
            } else if (href && href.toString) {
                href = href.toString();
            } else {
                href = '';
            }
        }
        
        // 確保參數是字符串類型
        href = href ? String(href) : '';
        title = title ? String(title) : '';
        text = text ? String(text) : '';
        
        console.log("處理後的 href:", href);
        
        // 處理圖片尺寸 (例如: image.jpg =300x200)
        let width = '';
        let height = '';
        const sizeParts = href.split(/\s*=\s*/);
        if (sizeParts.length > 1) {
            href = sizeParts[0];
            const sizeStr = sizeParts[1];
            const sizeMatch = sizeStr.match(/^(\d+)x(\d+)$/i);
            if (sizeMatch) {
                width = sizeMatch[1];
                height = sizeMatch[2];
                console.log(`檢測到圖片尺寸: ${width}x${height}`);
            }
        }
        
        // 處理不同類型的圖片路徑
        let imgUrl = href;
        
        try {
            // 排除無效的 URL
            if (!href || href === '[object Object]' || href === 'undefined') {
                throw new Error("無效的圖片URL");
            }
            
            // 如果是相對路徑（不包含http://或https://）
            if (!href.startsWith('http://') && !href.startsWith('https://')) {
                // 如果是舊的路徑格式 (/get-image/...)
                if (href.includes('/get-image/')) {
                    const filename = href.split('/').pop();
                    imgUrl = `${API_BASE_URL}/images/get/${filename}`;
                }
                // 如果是新的路徑格式但不完整 (/images/get/...)
                else if (href.includes('/images/get/')) {
                    if (!href.startsWith('http')) {
                        imgUrl = `${API_BASE_URL}${href.startsWith('/') ? '' : '/'}${href}`;
                    }
                }
                // 如果是文件名格式 (filename.jpg)
                else if (href.match(/\.(jpg|jpeg|png|gif|bmp|webp|PNG|JPG|JPEG|GIF)$/i)) {
                    imgUrl = `${API_BASE_URL}/images/get/${href}`;
                }
            }
            
            console.log("最終圖片URL:", imgUrl);
        } catch (error) {
            console.error("處理圖片URL時發生錯誤:", error);
            // 發生錯誤時使用預設錯誤圖片
            imgUrl = '';
        }
        
        // 使用資料 URL 作為預設圖片，避免外部請求
        const errorPlaceholder = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='200' viewBox='0 0 300 200'%3E%3Crect width='300' height='200' fill='%23eee'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='16' text-anchor='middle' dominant-baseline='middle' fill='%23999'%3E圖片載入錯誤%3C/text%3E%3C/svg%3E";
        
        // 構建樣式
        let style = 'max-width: 100%; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);';
        if (width) style += ` width: ${width}px;`;
        if (height) style += ` height: ${height}px;`;
        
        // 輸出帶有尺寸控制和錯誤處理的圖片標籤
        return `<img src="${imgUrl || errorPlaceholder}" alt="${text || '圖片'}" title="${title || ''}" onerror="this.onerror=null;this.src='${errorPlaceholder}';" style="${style}">`;
    };
    
    // 配置 Marked.js
    marked.setOptions({
        renderer: renderer,
        gfm: true,
        breaks: true,
        smartLists: true
    });
    
    // 初始化Material Components
    const buttons = document.querySelectorAll('.mdc-button');
    buttons.forEach(button => {
        mdc.ripple.MDCRipple.attachTo(button);
    });
    
    const textFields = document.querySelectorAll('.mdc-text-field');
    textFields.forEach(textField => {
        mdc.textField.MDCTextField.attachTo(textField);
    });
});

// 顯示/隱藏表單事件處理
if (document.getElementById('uploadImageBtn')) {
    document.getElementById('uploadImageBtn').addEventListener('click', () => {
        document.getElementById('imageUploadForm').style.display = 'block';
    });
}

if (document.getElementById('cancelUploadBtn')) {
    document.getElementById('cancelUploadBtn').addEventListener('click', () => {
        document.getElementById('imageUploadForm').style.display = 'none';
    });
}

if (document.getElementById('createNoteBtn')) {
    document.getElementById('createNoteBtn').addEventListener('click', () => {
        document.getElementById('markdownEditor').style.display = 'block';
        document.getElementById('markdownContent').value = '';
        currentEditingNoteId = null;
    });
}

if (document.getElementById('cancelEditBtn')) {
    document.getElementById('cancelEditBtn').addEventListener('click', () => {
        document.getElementById('markdownEditor').style.display = 'none';
        currentEditingNoteId = null;
    });
}

// 圖片上傳處理
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('imageFile');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${API_BASE_URL}/images/upload/`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        document.getElementById('imageResult').innerHTML = 
            `<div class="mdc-card">
                <p>圖片上傳成功！</p>
                <p>URL: <a href="${data.url}" target="_blank">${data.url}</a></p>
                <img src="${data.url}" style="max-width: 300px; margin-top: 10px;">
            </div>`;
        document.getElementById('imageUploadForm').style.display = 'none';
    } catch (error) {
        document.getElementById('imageResult').innerHTML = 
            `<div class="mdc-card" style="color: red;">
                <p>上傳失敗: ${error.message}</p>
            </div>`;
    }
});

// Markdown保存處理
document.getElementById('saveMarkdown').addEventListener('click', async () => {
    const content = document.getElementById('markdownContent').value;
    if (!content) {
        alert('請輸入Markdown內容');
        return;
    }

    try {
        console.log('開始保存文章...');
        
        // 判斷是新增還是更新
        let url, method;
        if (currentEditingNoteId) {
            url = `${API_BASE_URL}/notes/${currentEditingNoteId}`;
            method = 'PUT';
            console.log('更新現有文章:', currentEditingNoteId);
        } else {
            url = `${API_BASE_URL}/notes/create/`;
            method = 'POST';
            console.log('創建新文章');
        }
        
        // 使用更安全的Base64編碼方式
        const encoder = new TextEncoder();
        const bytes = encoder.encode(content);
        const contentBase64 = btoa(Array.from(bytes).map(b => String.fromCharCode(b)).join(''));
            
        console.log('內容編碼完成，準備發送請求...');
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: contentBase64
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        console.log('請求成功，狀態碼:', response.status);
        
        const data = await response.json();
        
        let message;
        if (currentEditingNoteId) {
            message = `<p>${data.message}</p>`;
        } else {
            message = `
                <p>${data.message}</p>
                <p>內容長度: ${data.content_length} 字元</p>
            `;
        }
        
        document.getElementById('markdownResult').innerHTML = 
            `<div class="mdc-card">${message}</div>`;
            
        document.getElementById('markdownEditor').style.display = 'none';
        currentEditingNoteId = null; // 重置編輯ID
        
        // 重新載入文章列表
        document.getElementById('getAllNotes').click();
    } catch (error) {
        console.error('保存文章失敗:', error);
        document.getElementById('markdownResult').innerHTML = 
            `<div class="mdc-card" style="color: red;">
                <p>儲存失敗: ${error.message}</p>
            </div>`;
    }
});

// 获取所有图片
document.getElementById('getAllImages').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/images/all/`);
        const data = await response.json();
        console.log("API返回圖片數據:", data); // 調試用
        
        let imagesHTML = '<h3>所有圖片</h3><div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px;">';
        
        // 添加檢查确保data.images是數組且非空
        if (data.images && Array.isArray(data.images) && data.images.length > 0) {
            data.images.forEach(img => {
                // 從數組中獲取文件名 (img[1])
                const filename = img && img[1] ? img[1] : '';
                
                // 只有當文件名非空時才顯示圖片
                if (filename) {
                    // 使用文件名直接構建新的URL路徑
                    const imgUrl = `${API_BASE_URL}/images/get/${filename}`;
                    console.log("構建圖片URL:", imgUrl); // 調試用
                    
                    imagesHTML += `
                    <div class="mdc-card image-card">
                        <img src="${imgUrl}" style="width: 100%; height: 200px; object-fit: cover;" onerror="this.src='https://via.placeholder.com/300x200?text=圖片載入錯誤'">
                        <div class="mdc-card__actions" style="justify-content: flex-end; padding: 8px;">
                            <button class="mdc-button mdc-button--raised mdc-button--error" onclick="deleteImage('${filename}')">
                                <i class="material-icons mdc-button__icon">delete</i>
                                <span class="mdc-button__label">刪除</span>
                            </button>
                        </div>
                        <div class="mdc-card__content" style="padding: 8px;">
                            <p>${filename}</p>
                        </div>
                    </div>`;
                }
            });
        } else {
            imagesHTML += '<p>沒有找到圖片</p>';
        }
        
        imagesHTML += '</div>';
        
        document.getElementById('imagesContainer').innerHTML = imagesHTML;
    } catch (error) {
        document.getElementById('imagesContainer').innerHTML = 
            `<div class="mdc-card" style="color: red;">
                <p>取得圖片失敗: ${error.message}</p>
            </div>`;
    }
});

// 获取所有文章
document.getElementById('getAllNotes').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/notes/all/`);
        const data = await response.json();
        console.log("API返回文章數據:", data);  // 調試用
        
        let notesHTML = '<h3>所有文章</h3><div style="display: flex; flex-direction: column; gap: 15px;">';
        
        // 確保notes是數組且非空
        if (data.notes && Array.isArray(data.notes) && data.notes.length > 0) {
            data.notes.forEach(note => {
                // 處理標籤顯示（如果有）
                let tagsHtml = '';
                if (note.tags && note.tags.length > 0) {
                    tagsHtml = '<div class="tags" style="margin-top: 10px;">';
                    note.tags.forEach(tag => {
                        tagsHtml += `<span style="background: #eee; padding: 2px 8px; border-radius: 12px; margin-right: 5px; font-size: 14px;">${tag}</span>`;
                    });
                    tagsHtml += '</div>';
                }
                
                // 檢查note.content是否存在
                const content = note.content || '';
                
                // 使用自定義渲染器解析Markdown
                const parsedContent = marked.parse(content);
                console.log(`解析文章ID ${note.id} Markdown`);  // 調試用
                
                notesHTML += `
                <div class="mdc-card note-card">
                    <div class="mdc-card__content">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <span><strong>ID:</strong> ${note.id}</span>
                            <span><strong>建立時間:</strong> ${note.created_at}</span>
                        </div>
                        <div style="border-top: 1px solid #eee; padding-top: 10px;">
                            ${parsedContent}
                        </div>
                        ${tagsHtml}
                    </div>
                    <div class="mdc-card__actions" style="justify-content: flex-end;">
                        <button class="mdc-button mdc-button--outlined" onclick="editNote('${note.id}')">
                            <i class="material-icons mdc-button__icon">edit</i>
                            <span class="mdc-button__label">編輯</span>
                        </button>
                        <button class="mdc-button mdc-button--outlined mdc-button--error" onclick="deleteNote('${note.id}')">
                            <i class="material-icons mdc-button__icon">delete</i>
                            <span class="mdc-button__label">刪除</span>
                        </button>
                    </div>
                </div>`;
            });
        } else {
            notesHTML += '<p>沒有找到文章</p>';
        }
        
        notesHTML += '</div>';
        
        document.getElementById('notesContainer').innerHTML = notesHTML;
    } catch (error) {
        document.getElementById('notesContainer').innerHTML = 
            `<div class="mdc-card" style="color: red;">
                <p>取得文章失敗: ${error.message}</p>
            </div>`;
    }
});

// 全局函數
// 刪除圖片
function deleteImage(filename) {
    if (!filename) {
        alert('無效的檔案名稱');
        return;
    }
    
    if (!confirm('確定要刪除此圖片嗎？')) return;
    
    try {
        fetch(`${API_BASE_URL}/images/delete/${filename}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            document.getElementById('getAllImages').click();
        })
        .catch(error => {
            alert(`刪除失敗: ${error.message}`);
        });
    } catch (error) {
        alert(`刪除失敗: ${error.message}`);
    }
}

// 刪除文章
function deleteNote(id) {
    if (!confirm('確定要刪除此文章嗎？')) return;
    
    try {
        fetch(`${API_BASE_URL}/notes/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            document.getElementById('getAllNotes').click();
        })
        .catch(error => {
            alert(`刪除失敗: ${error.message}`);
        });
    } catch (error) {
        alert(`刪除失敗: ${error.message}`);
    }
}

// 編輯文章
function editNote(id) {
    try {
        fetch(`${API_BASE_URL}/notes/${id}`)
        .then(response => response.json())
        .then(data => {
            // 檢查返回的資料格式 (適配新的API格式)
            if (data.note && data.note.content) {
                const content = data.note.content;
                
                // 記錄當前編輯的文章ID
                currentEditingNoteId = id;
                
                // 顯示編輯器並設定內容
                document.getElementById('markdownContent').value = content;
                document.getElementById('markdownEditor').style.display = 'block';
            } else {
                alert('文章格式錯誤');
            }
        })
        .catch(error => {
            alert(`取得文章失敗: ${error.message}`);
        });
    } catch (error) {
        alert(`取得文章失敗: ${error.message}`);
    }
}

// 檔案管理相關功能
function initializeFileUpload() {
    console.log('初始化檔案上傳功能');
    
    // 綁定檔案列表載入按鈕
    const getAllFilesBtn = document.getElementById('getAllFiles');
    console.log('getAllFiles按鈕元素:', getAllFilesBtn);
    
    if (getAllFilesBtn) {
        getAllFilesBtn.addEventListener('click', getAllFiles);
        console.log('已綁定getAllFiles事件');
        // 頁面載入時自動獲取
        getAllFiles();
    }

    // 綁定檔案上傳按鈕
    const uploadFileBtn = document.getElementById('uploadFileBtn');
    console.log('uploadFileBtn元素:', uploadFileBtn);
    
    if (uploadFileBtn) {
        uploadFileBtn.addEventListener('click', uploadFile);
        console.log('已綁定uploadFile事件');
    }
}

// 獲取所有檔案
function getAllFiles() {
    console.log('開始獲取所有檔案');
    const filesListEl = document.getElementById('filesList');
    console.log('filesList元素:', filesListEl);
    
    if (!filesListEl) {
        console.warn('找不到filesList元素');
        return;
    }

    filesListEl.innerHTML = '<div class="loading-message">載入中...</div>';

    console.log('發送請求到:', `${API_BASE_URL}/files/all/`);
    fetch(`${API_BASE_URL}/files/all/`)
        .then(response => {
            console.log('獲取檔案列表回應:', response);
            return response.json();
        })
        .then(data => {
            console.log('獲取檔案列表數據:', data);
            if (data.files && Array.isArray(data.files)) {
                console.log(`找到 ${data.files.length} 個檔案`);
                displayFiles(data.files);
            } else {
                console.warn('未找到檔案或格式不正確:', data);
                filesListEl.innerHTML = '<div class="loading-message">沒有找到檔案</div>';
            }
        })
        .catch(error => {
            console.error('獲取檔案列表失敗:', error);
            filesListEl.innerHTML = `<div class="loading-message">載入失敗: ${error.message}</div>`;
        });
}

// 顯示檔案列表
function displayFiles(files) {
    console.log('開始顯示檔案列表:', files);
    
    const filesListEl = document.getElementById('filesList');
    if (!filesListEl) {
        console.warn('找不到檔案列表容器');
        return;
    }

    if (!files || files.length === 0) {
        console.log('沒有檔案要顯示');
        filesListEl.innerHTML = '<div class="loading-message">尚未上傳任何檔案</div>';
        return;
    }

    // 清空列表
    filesListEl.innerHTML = '';
    console.log(`準備顯示 ${files.length} 個檔案`);

    // 添加每個檔案卡片
    files.forEach((file, index) => {
        console.log(`處理第 ${index + 1} 個檔案:`, file);
        try {
            const fileCard = createFileCard(file);
            filesListEl.appendChild(fileCard);
        } catch (error) {
            console.error(`創建檔案卡片失敗 (${file.filename}):`, error);
        }
    });
}

// 創建檔案卡片
function createFileCard(file) {
    console.log('創建檔案卡片:', file);
    
    const fileCard = document.createElement('div');
    fileCard.className = 'file-card';
    fileCard.dataset.fileId = file.id;

    try {
        const iconName = getFileIconByType(file.type);
        const fileSize = formatFileSize(file.size);
        const isPreviewable = ['image', 'video'].includes(file.type);
        
        const previewButton = isPreviewable ? `
            <button onclick="previewMedia('/files/download/${file.filename}', '${file.original_filename}', '${file.type}')" class="preview-button">
                ${file.type === 'video' ? '播放' : '預覽'}
            </button>
        ` : '';

        fileCard.innerHTML = `
            <div class="file-icon">
                <i class="material-icons">${iconName}</i>
            </div>
            <div class="file-info">
                <div class="file-name" title="${file.original_filename}">${file.original_filename}</div>
                <div class="file-size">${fileSize}</div>
            </div>
            <div class="file-actions">
                <a href="/files/download/${file.filename}" class="mdc-button mdc-button--outlined" target="_blank">
                    <span class="mdc-button__label">下載</span>
                </a>
                ${previewButton}
                <button onclick="shareFile(${file.id})" class="mdc-button mdc-button--outlined">
                    <i class="material-icons mdc-button__icon">share</i>
                    <span class="mdc-button__label">分享</span>
                </button>
                <button onclick="deleteFile(${file.id})" class="mdc-button mdc-button--outlined">
                    <i class="material-icons mdc-button__icon">delete</i>
                    <span class="mdc-button__label">刪除</span>
                </button>
            </div>
        `;
        
        return fileCard;
    } catch (error) {
        console.error('創建檔案卡片時發生錯誤:', error);
        throw error;
    }
}

// 取得檔案類型對應的 icon
function getFileIconByType(fileType) {
    console.log('取得檔案圖標，檔案類型:', fileType);
    
    if (!fileType) {
        console.warn('未提供檔案類型，使用預設圖標');
        return 'insert_drive_file';
    }
    
    const iconMap = {
        'image': 'image',
        'video': 'video_library',
        'audio': 'audio_file',
        'document': 'description',
        'archive': 'folder_zip',
        'pdf': 'picture_as_pdf'
    };

    const icon = iconMap[fileType] || 'insert_drive_file';
    console.log(`檔案類型 ${fileType} 對應的圖標:`, icon);
    return icon;
}

// 格式化檔案大小
function formatFileSize(bytes) {
    if (bytes < 1024) {
        return bytes + ' B';
    } else if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(1) + ' KB';
    } else if (bytes < 1024 * 1024 * 1024) {
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    } else {
        return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
    }
}

// 上傳檔案
async function uploadFile() {
    console.log('開始上傳檔案');
    const fileInput = document.getElementById('fileInput');
    console.log('fileInput元素:', fileInput);
    
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        console.warn('未選擇檔案');
        alert('請選擇一個檔案');
        return;
    }

    const file = fileInput.files[0];
    console.log('選擇的檔案:', {
        name: file.name,
        size: file.size,
        type: file.type
    });

    const formData = new FormData();
    formData.append('file', file);

    try {
        console.log('發送上傳請求到:', `${API_BASE_URL}/files/upload/`);
        const response = await fetch(`${API_BASE_URL}/files/upload/`, {
            method: 'POST',
            body: formData
        });

        console.log('上傳回應狀態:', response.status);
        if (!response.ok) {
            throw new Error(`上傳失敗: ${response.status}`);
        }

        const result = await response.json();
        console.log('上傳成功，伺服器回應:', result);
        
        // 重新載入檔案列表
        getAllFiles();
        
        // 清空輸入
        fileInput.value = '';
        console.log('已清空檔案輸入框');
    } catch (error) {
        console.error('上傳失敗:', error);
        alert(`上傳失敗: ${error.message}`);
    }
}

// 刪除檔案
async function deleteFile(fileId) {
    console.log('準備刪除檔案:', fileId);
    
    if (!confirm('確定要刪除此檔案嗎？')) {
        console.log('使用者取消刪除操作');
        return;
    }

    try {
        console.log('發送刪除請求到:', `${API_BASE_URL}/files/${fileId}`);
        const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
            method: 'DELETE'
        });

        console.log('刪除回應狀態:', response.status);
        if (!response.ok) {
            throw new Error(`刪除失敗: ${response.status}`);
        }

        console.log('檔案刪除成功');
        // 重新載入檔案列表
        getAllFiles();
    } catch (error) {
        console.error('刪除失敗:', error);
        alert(`刪除失敗: ${error.message}`);
    }
}

// 預覽媒體檔案
function previewMedia(fileUrl, fileName, fileType) {
    console.log('預覽媒體檔案:', {
        url: fileUrl,
        name: fileName,
        type: fileType
    });
    
    const mediaDialog = document.getElementById('mediaDialog');
    const videoPlayer = document.getElementById('videoPlayer');
    const imageViewer = document.getElementById('imageViewer');
    const mediaTitle = document.querySelector('.media-title');

    console.log('預覽對話框元素:', mediaDialog);
    console.log('影片播放器元素:', videoPlayer);
    console.log('圖片檢視器元素:', imageViewer);

    mediaDialog.style.display = 'block';
    mediaTitle.textContent = fileName;

    if (fileType === 'video') {
        console.log('播放影片');
        videoPlayer.style.display = 'block';
        imageViewer.style.display = 'none';
        videoPlayer.src = fileUrl;
        videoPlayer.play();
    } else if (fileType === 'image') {
        console.log('顯示圖片');
        videoPlayer.style.display = 'none';
        imageViewer.style.display = 'block';
        imageViewer.src = fileUrl;
    }
}

// 分享文件
async function shareFile(fileId) {
    try {
        console.log('創建分享連結:', fileId);
        
        const response = await fetch(`${API_BASE_URL}/share/create/${fileId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const shareUrl = window.location.origin + data.url;
        
        // 複製連結到剪貼簿
        navigator.clipboard.writeText(shareUrl).then(() => {
            alert('分享連結已複製到剪貼簿：\n' + shareUrl);
        }).catch(() => {
            // 如果剪貼簿API失敗，至少顯示連結
            alert('分享連結（請手動複製）：\n' + shareUrl);
        });
        
    } catch (error) {
        console.error('分享失敗:', error);
        alert(`分享失敗: ${error.message}`);
    }
}

// 複製分享連結
function copyShareUrl(url) {
    const input = document.getElementById('shareUrl');
    input.select();
    document.execCommand('copy');
    alert('已複製分享連結到剪貼簿！');
}

// 關閉分享對話框
function closeShareDialog() {
    const dialog = document.querySelector('.share-dialog');
    if (dialog) {
        dialog.remove();
    }
}