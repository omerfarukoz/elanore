const messageArea = document.getElementById('messagearea');

function scrollToBottom() {
    messageArea.scrollTop = messageArea.scrollHeight;
}


document.getElementById('msgsend_id').addEventListener('click', () => {
const inputText = document.getElementById('msgbox_id').value;
document.getElementById('msgbox_id').value = "";

const url = '/api/chat/' + session_key;
const formData = new FormData();
formData.append('prompt', inputText);
document.getElementById("messagearea").innerHTML += `
<div class="message  message-out ">

<div class="message-inner">
    <div class="message-body">
        <div class="message-content">
            <div class="message-text">
                <p>` + inputText +`</p>
            </div>
        </div>
    </div>
</div>
</div>
<div class="py-12 py-lg-12">
<div class="message">
        <a href="#" data-bs-toggle="modal" data-bs-target="#modal-user-profile" class="avatar avatar-responsive">
            <img class="avatar-img" src="/assets/img/logo.png" alt="">
        </a>

        <div class="message-inner">
            <div class="message-body">
                <div class="message-content">
                    <div class="message-text">
                        <p><span id="response_msg"><span><span class="typing-dots"><span>.</span><span>.</span><span>.</span></span></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>


`;
scrollToBottom();

fetch(url, {
    method: 'POST',
    body: formData,
})
.then((response) => {
    if (!response.ok) {
        throw new Error('Ağ hatası');
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    var all_message = "";
    function read() {
        return reader.read().then(({ done, value }) => {
            if (done) {
                console.log('Akış tamamlandı.');
                document.getElementById("response_msg").removeAttribute("id");
                return;
            }
            const chunk = decoder.decode(value, { stream: true });
            const parts = chunk.split('\n'); 
            parts.forEach(part => {
                if (part) { 
                    try {
                        const jsonResponse = JSON.parse(part);
                        console.log('JSON Yanıt:', jsonResponse);
                        sessionkey = jsonResponse["session"];
                        all_message += jsonResponse["llama_response"];
                        document.getElementById("response_msg").innerHTML=all_message;
                    } catch (e) {
                        console.error('Geçersiz JSON:', e);
                    }
                }
            });
            read();
        });
    }

    read(); 
})
.catch((error) => {
    console.error('Hata:', error);
});
});""



window.onload = scrollToBottom();
