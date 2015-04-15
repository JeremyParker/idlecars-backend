var app = angular.module('app',[]);

app.controller('formCtrl', function($scope){

	$scope.zipBind = 'Zip Code:';
	$scope.emailBind = 'Email:';

	$scope.val = function(event){
		var zipcode_required = $scope.myForm.zipcode.$error.required;
		var zipcode_pattern = $scope.myForm.zipcode.$error.pattern;
		var email_required = $scope.myForm.email.$error.required;
		var email_invalid = $scope.myForm.email.$invalid;

		// zip code input validation
		if (zipcode_required) {
			$scope.zipBind = '*Zipcode is required';
			$scope.zipRed = true;
			event.preventDefault();
			
		}
		else if (zipcode_pattern) {
			$scope.zipBind = '*Please enter a valid zip code';
			$scope.zipRed = true;
			event.preventDefault();
		}
		else{
			$scope.zipBind = 'Zipcode:';
			$scope.zipRed = false;
			
		};

		// email input validation
		if (email_required) {
			$scope.emailBind = '*Email is required';
			$scope.emailRed = true;
			event.preventDefault();
		}
		else if (email_invalid) {
			$scope.emailBind = '*Please enter a valid email';
			$scope.emailRed = true;
			event.preventDefault();
		}
		else{
			$scope.emailBind = 'Email:';
			$scope.emailRed = false;
		};
	}
	
})