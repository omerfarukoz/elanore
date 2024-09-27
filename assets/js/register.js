const form = document.querySelector("#registerform");

async function sendData() {
  const formData = new FormData(form);

  try {
    const response = await fetch("/api/register", {
      method: "POST",
      body: formData,
    });
    response_json = await response.json();
    status_text = "Error !";
    status_img = 'assets/svg/attention.svg';
    if(response_json["status"]){
        status_text == "Success !";
        status_img = 'assets/svg/check.svg';
        window.location.href = "/home";
    }


    document.getElementById("statusdiv").innerHTML = `
        <div class="card border-0">
            <div class="card-body">

                <div class="row align-items-center gx-5">
                    <div class="col-auto">
                        <a href="#" class="avatar ">
                            <img class="avatar-img" src="`+status_img+`" alt="">
                        </a>
                    </div>

                    <div class="col">
                        <h5><a href="#">`+status_text+`</a></h5>
                        <p>` + response_json["message"] +`</p>
                    </div>



                </div>

            </div>
        </div>    
        `; 
    

  } catch (e) {
    console.error(e);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendData();
});