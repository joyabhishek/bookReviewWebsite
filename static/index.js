document.addEventListener('DOMContentLoaded',() => {


   document.querySelector('#searchText').onclick = function(){
     document.querySelectorAll('.dropdown-item').forEach(function(a){
            console.log("Nikal rhe hai ...")
            a.remove();
        })
        const div = document.querySelector('#dropDownMenu');
        div.style.display = "none";
    };


    document.querySelector('#search').onsubmit = () => {
        document.querySelectorAll('.dropdown-item').forEach(function(a){
            console.log("Nikal rhe hai ...")
            a.remove();
        })
        const div = document.querySelector('#dropDownMenu');
        div.style.display = "none";
        const request = new XMLHttpRequest();
        searchText = document.querySelector('#searchText').value;
        console.log(searchText)
        request.open('POST', '/search');
        request.onload = () => {
            const data = JSON.parse(request.responseText);
            console.log(data);          
            if (data.response){
                console.log(data.booknameList);
                if (data.booknameList.length > 0){
                    for (bookname in data.booknameList){
                        console.log(data.booknameList[bookname]);                   
                        const a = document.createElement('a');
                        a.innerHTML = data.booknameList[bookname]['title'];
                        a.href = '/book/'.concat(data.booknameList[bookname]['isbn'])
                        a.classList.add("dropdown-item");
                        div.appendChild(a);                 
                    }
                    div.style.display = "block";
                    document.querySelector('#searchText').value = '';                   
                }else{
                    const p = document.createElement('p');
                    p.innerHTML = 'Nhi mila kuch';
                    p.classList.add("dropdown-item");
                    div.appendChild(p);
                    div.style.display = "block";
                    document.querySelector('#searchText').value = '';
                }
            }else{
                const div = document.querySelector('#dropDownMenu');
                const p = document.createElement('p');
                p.innerHTML = 'Sorry try again';
                p.classList.add("dropdown-item");
                div.appendChild(p);
                div.style.display = "block";
                document.querySelector('#searchText').value = '';
            }

        }

        const data = new FormData();
        data.append('searchText',searchText);
        request.send(data);
        return false;

    }
})