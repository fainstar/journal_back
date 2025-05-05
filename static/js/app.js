// 全局變數
let currentEditingNoteId = null;
const API_BASE_URL = 'http://127.0.0.1:8000';

// 初始化 Marked.js 和 Material Components
document.addEventListener('DOMContentLoaded', () => {
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
document.getElementById('uploadImageBtn').addEventListener('click', () => {
    document.getElementById('imageUploadForm').style.display = 'block';
});

document.getElementById('cancelUploadBtn').addEventListener('click', () => {
    document.getElementById('imageUploadForm').style.display = 'none';
});

document.getElementById('createNoteBtn').addEventListener('click', () => {
    document.getElementById('markdownEditor').style.display = 'block';
    document.getElementById('markdownContent').value = '';
    // 重置編輯ID，表示這是一篇新文章
    currentEditingNoteId = null;
});

document.getElementById('cancelEditBtn').addEventListener('click', () => {
    document.getElementById('markdownEditor').style.display = 'none';
    currentEditingNoteId = null; // 取消時也重置編輯ID
});

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
        // 判斷是新增還是更新
        let url, method;
        if (currentEditingNoteId) {
            // 更新現有文章
            url = `${API_BASE_URL}/notes/${currentEditingNoteId}`;
            method = 'PUT';
        } else {
            // 新增文章
            url = `${API_BASE_URL}/notes/create/`;
            method = 'POST';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: btoa(unescape(encodeURIComponent(content)))
            })
        });
        
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