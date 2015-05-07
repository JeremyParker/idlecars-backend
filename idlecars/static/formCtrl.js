var app = angular.module('app',[]);

app.controller('formCtrl', function($scope){

  $scope.zipLabel = 'Zip Code:';
  $scope.emailLabel = 'Email:';

  $scope.validation = function(event){
    var emailIsValid = validateEmail();
    var zipcodeIsValid = validateZipcode();
    if (!(emailIsValid && zipcodeIsValid)) {
        event.preventDefault();
    }
  }

  var validateZipcode = function(){
    var zipcodeIsEmpty = $scope.myForm.zipcode.$error.required;
    var zipcodeIsInvalid = $scope.myForm.zipcode.$error.pattern;

    if (zipcodeIsEmpty) {
      $scope.zipLabel = 'Zipcode is required';
      $scope.zipRed = true;
    }
    else if (zipcodeIsInvalid) {
      $scope.zipLabel = 'Please enter a valid zip code';
      $scope.zipRed = true;
    }
    else{
      $scope.zipLabel = 'Zipcode:';
      $scope.zipRed = false;
    }

    return !zipcodeIsEmpty && !zipcodeIsInvalid;
  };

  var validateEmail = function(){
    var emailIsEmpty = $scope.myForm.email.$error.required;
    var emailIsInvalid = $scope.myForm.email.$invalid;

    if (emailIsEmpty) {
      $scope.emailLabel = 'Email is required';
      $scope.emailRed = true;
      event.preventDefault();
    }
    else if (emailIsInvalid) {
      $scope.emailLabel = 'Please enter a valid email';
      $scope.emailRed = true;
      event.preventDefault();
    }
    else{
      $scope.emailLabel = 'Email:';
      $scope.emailRed = false;
    }

    return !emailIsEmpty && !emailIsInvalid;
  };

});
