function LoginOrRegistration(){
    var login = document.getElementById('login').value; 
    var password = document.getElementById('password').value; 
    var admin = document.getElementById('admin').value; 
    var is_admin = false;
    if (admin == "admin"){
        is_admin = true;
    }

    const body = JSON.stringify({body : {
        login: login,
        password: password,
        is_admin: is_admin
    }
    });

    res = SendRequestPost(body, "http://127.0.0.1:8000/add_user");
    console.log(res);
    token = JSON.parse(res).token;
    document.getElementById("storage").innerHTML = token;
    ShowListTask()
}

function ReadTask(path){
    token = document.getElementById("storage");
    console.log(token);
    if (token == null){
        var text = document.getElementById("ReloginField");
        text.style.display = "block";
    }
    else {
        var task_name = document.getElementById('task_name').value; 
        const body = JSON.stringify({body : {
            token: token,
            task_name: task_name
        }
        });
        res = SendRequestPost(body, path);
        ShowListTask()
    }
}

function AddTask(){
    ReadTask("http://127.0.0.1:8000/add_task")
}

function EditTask(){
    ReadTask("http://127.0.0.1:8000/edit_task")
}

function DeleteTask(){
    ReadTask("http://127.0.0.1:8000/delete_task")
}

function ShowListTask(){
    token = document.getElementById("storage");
    if (token == null){
        var text = document.getElementById("ReloginField");
        text.style.display = "block";
    }
    else{
        const body = JSON.stringify({body : {
            token: token
        }
        });
        res = SendRequestGet(body, "http://127.0.0.1:8000/get_list_tasks")
        var tasks = JSON.parse(res);
        for (var task in tasks) {
            document.getElementById('tasks-list').innerHTML += '<li>' + task.task_name + '</li>';
        }
    }
}

function SendRequestGet(body, path)
{
    const resp = fetch(path, {
        mode: 'no-cors',
        method: "GET",
        body,
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
        })
        return resp.json();
}

function SendRequestPost(body, path)
{
    res = fetch(path, {
    mode: 'no-cors',
    method: "POST",
    body,
    headers: {
        "Content-type": "application/json; charset=UTF-8"
    }
    })
    return res.response.json();
}
