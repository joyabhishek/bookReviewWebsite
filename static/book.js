document.addEventListener('DOMContentLoaded',() => {
	document.querySelector('#reviewForm').onsubmit = () => {

		const reviewText = document.querySelector('#inputReviewText').value;
		const rating = document.querySelector('#inputRating').value;
		const isbn = document.querySelector('#isbn').innerText;
		console.log("reviewText:"+reviewText+" rating:"+rating+" isbn:"+isbn)
		const request = new XMLHttpRequest()
		request.open("POST",'/addReview');

		request.onload = () => {
			const data = JSON.parse(request.responseText);
			console.log(data);

			if (data.response){
				document.querySelector('#reviewForm').style.display = "none";
				document.querySelector('#userReviewDetails').style.display = "block";
				document.querySelector('#username').innerHTML = "User: "+data.username;
				document.querySelector('#reviewText').innerHTML = "Review: "+reviewText;
				document.querySelector('#rating').innerHTML = "Rating: "+rating;
				
			}else{
				alert('Cannot submit your review!!!')
			}

		}

		const data = new FormData()
		data.append('reviewText',reviewText);
		data.append('rating',rating);
		data.append('isbn',isbn);
		request.send(data);
		return false;
	}
})