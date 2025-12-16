function saveRecord() {
    var autoSaveCssClass = document.querySelector('div.autoSaveScript');

    if (!autoSaveCssClass) {
        return;
    }

    var saveButton = document.querySelector(".o_form_button_save");

    if (saveButton){
        saveButton.click();
        console.log("autoSaveScript: Button with class 'o_form_button_save' clicked.");
    } else {
        console.warn("autoSaveScript: No button with class 'o_form_button_save' found.");
    }
}

setInterval(saveRecord, 500);
