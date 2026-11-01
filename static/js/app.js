function copyShortUrl() {
    const input = document.getElementById("shortUrlInput");
    if (!input) return;

    input.select();
    input.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(input.value).then(() => {
        const btnText = document.getElementById("copyBtnText");
        if (btnText) {
            const original = btnText.textContent;
            btnText.textContent = "Скопировано!";
            setTimeout(() => {
                btnText.textContent = original;
            }, 2000);
        }
    }).catch(() => {
        document.execCommand("copy");
    });
}
