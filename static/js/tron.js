var tronApp = angular.module('tronApp', ['ngMaterial', 'ngMessages', 'angular-cron-jobs', 'satellizer']);

tronApp.config(['$interpolateProvider', function ($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

tronApp.config(['$authProvider', function ($authProvider) {
  $authProvider.github({
    clientId: 'e031c7767d9f969219e9',
  });
}]);

tronApp.controller('tronCtrl', function($scope, $http, $mdDialog, $auth) {

  $scope.isAuthenticated = false;

  $scope.login = function () {
    $auth.authenticate('github').then(function (response) {
      $scope.isAuthenticated = true;
    });
  }

  $scope.logout = function () {
    $auth.logout().then(function (response) {
      $scope.isAuthenticated = false;
    });
  }

  $scope.selectedRepo = undefined;
  $scope.cronConfig = {
    options: {
      allowMinute: false,
      allowHour: false,
    },
  }
  $scope.cronOutput;

  $scope.addNewJobDialog = function (event) {
    var promise = $mdDialog.show({
      templateUrl: 'job/',
      parent: angular.element(document.body),
      targetEvent: event,
      clickOutsideToClose: true,
      scope: $scope,
      preserveScope: true,
    })
    
    promise.then(
      function(answer) {
        $scope.status = 'You said the information was "' + answer + '".';
      },
      function() {
        $scope.status = 'You cancelled the dialog.';
      }
    );
  }

  $scope.jobDetailsDialog = function () {}

});
