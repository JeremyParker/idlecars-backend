var app = angular.module('app',[]);

app.controller('formCtrl', function ($scope) {

  $scope.nameLabel = 'First name:';
  $scope.emailLabel = 'Email:';
  $scope.messageLabel = 'Message:';

  $scope.validation = function(event){
    var emailIsValid = validateEmail();
    var nameIsValid = validateName();
    var messageIsValid = validateMessage();

    if (!(emailIsValid && nameIsValid && messageIsValid)) {
      event.preventDefault();
    }
  }

  var validateMessage = function () {
    var messageIsEmpty= $scope.myForm.message.$error.required;

    if (messageIsEmpty) {
      $scope.messageLabel = 'Message is required';
      $scope.messageRed = true;
    }
    else {
      $scope.messageLabel = 'Message:';
      $scope.messageRed = false;
    }

    return !messageIsEmpty;
  };

  var validateName = function () {
    var nameIsEmpty= $scope.myForm.first_name.$error.required;

    if (nameIsEmpty) {
      $scope.nameLabel = 'First name is required';
      $scope.nameRed = true;
    }
    else {
      $scope.nameLabel = 'First name:';
      $scope.nameRed = false;
    }

    return !nameIsEmpty;
  };

  var validateEmail = function(){
    var emailIsEmpty = $scope.myForm.email.$error.required;
    var emailIsInvalid = $scope.myForm.email.$invalid;

    if (emailIsEmpty) {
      $scope.emailLabel = 'Email is required';
      $scope.emailRed = true;
    }
    else if (emailIsInvalid) {
      $scope.emailLabel = 'Please enter a valid email';
      $scope.emailRed = true;
    }
    else{
      $scope.emailLabel = 'Email:';
      $scope.emailRed = false;
    }

    return !emailIsEmpty && !emailIsInvalid;
  };

});
