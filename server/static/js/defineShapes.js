
function initializeArray(rows, cols) {
    return Array(rows).fill(0).map(() => Array(cols).fill(0));
}

function handleClick(row, col) {

    let cell = document.getElementById(`cell_${row}_${col}`);
    shapeArray[row][col] = shapeArray[row][col] ? 0 : 1;
    if( shapeArray[row][col] ){
        cell.classList.add("bg-primary");
    } else {
        cell.classList.remove("bg-primary");
    }
    console.log(shapeArray);

}

let rows_all =  document.getElementsByClassName("cell-row");
let rows_total = rows_all.length
let columns_total = rows_all[0].children.length
console.log("rows: " + rows_total);
console.log("columns: " + columns_total);

let shapeArray = initializeArray(rows_total,columns_total);

function handleSubmit(modelIdx) {

    let request = new XMLHttpRequest();
    request.open("POST", `/define-shapes/${modelIdx}`, true);
    request.setRequestHeader("Content-type","application/x-www-form-urlencoded");

    request.onload = function() {
        let response = JSON.parse(this.responseText);
        if (response.status === "OK") {
            showToast();
            let nextModelId = parseInt(modelIdx)+1;
            setTimeout(function(){
                console.log("redirecting to next model...");
                window.location.href = '/define-shapes/'+nextModelId;
            }, 500);

        }
    }

    request.send(JSON.stringify(shapeArray));
}

function handleBackButton(modelIdx) {
    console.log(`redirect to last page`);
    let lastModelId = parseInt(modelIdx) - 1;
    if (lastModelId === -1) {
        window.location.href = '/upload-hydrus';
    } else {
        window.location.href = '/define-shapes/' + lastModelId;
    }
}

function showToast() {
    let myAlert = document.getElementById('successMessage');
    let bsAlert = new bootstrap.Toast(myAlert);
    bsAlert.show();
}
