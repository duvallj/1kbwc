function playSetup(event) {
    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the image and insert it inside the modal - use its "alt" text as a caption
    var img = document.getElementById("inspect-image");
    var modalImg = document.getElementById("img01");
    var captionText = document.getElementById("caption");
    img.onclick = function () {
        // TODO: also have the modal request a high-resolution image maybe?
        // (sorry currently the image resolutions are nuked to around 400px wide)
        modal.style.display = "block";
        modalImg.src = this.src;
        captionText.innerHTML = this.alt;
    }

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    span.onclick = function () {
        modal.style.display = "none";
    } 
    
    /// Send command on enter.
    input.addEventListener("keyup", function (event) {
        switch (event.keyCode) {
            case 13:  // Enter
                event.preventDefault();
                document.getElementById("submit").click();
                break;
        }
    });
    input.addEventListener("keydown", function (event) {
        switch (event.keyCode) {
            case 38:  // Up
                event.preventDefault();
                historyIndex = Math.min(historyIndex + 1, commandHistory.length - 1);
                historyUpdate();
                break;
            case 40:  // Down arrow
                event.preventDefault();
                historyIndex = Math.max(historyIndex - 1, -1);
                historyUpdate();
                break;
            case 27:  // Esc
                historyIndex = -1;
                historyBuffer = "";
                historyUpdate();
                break;
            default:
                if (historyIndex === -1) {
                    historyBuffer = input.value;
                }
        }
    });
}
