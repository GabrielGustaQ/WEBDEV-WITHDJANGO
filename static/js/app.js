document.addEventListener("DOMContentLoaded", function () {
    const deleteLinks = document.querySelectorAll("a[href*='excluir'], a[href*='cancelar']");

    deleteLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            const confirmed = confirm("Deseja continuar com esta ação?");
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});