var app = angular.module('app',[]);

app.controller('formCtrl', function($scope){

  $scope.zipLabel = 'Zip Code:';
  $scope.emailLabel = 'Email:';

  $scope.validation = function(event){

  $scope.validateZipCode();
  $scope.validateEmail();
  }

  $scope.validateZipCode = function(){

    var zipcode_required = $scope.myForm.zipcode.$error.required;
    var zipcode_pattern = $scope.myForm.zipcode.$error.pattern;

    // zip code input validation
    if (zipcode_required) {
      $scope.zipLabel = 'Zipcode is required';
      $scope.zipRed = true;
      event.preventDefault();

    }
    else if (zipcode_pattern) {
      $scope.zipLabel = 'Please enter a valid zip code';
      $scope.zipRed = true;
      event.preventDefault();
    }
    else{
      $scope.zipLabel = 'Zipcode:';
      $scope.zipRed = false;
    };
  }

    $scope.validateEmail = function(){

    var email_required = $scope.myForm.email.$error.required;
    var email_invalid = $scope.myForm.email.$invalid;

    // email input validation
    if (email_required) {
      $scope.emailLabel = 'Email is required';
      $scope.emailRed = true;
      event.preventDefault();
    }
    else if (email_invalid) {
      $scope.emailLabel = 'Please enter a valid email';
      $scope.emailRed = true;
      event.preventDefault();
    }
    else{
      $scope.emailLabel = 'Email:';
      $scope.emailRed = false;
    };
  }

})
