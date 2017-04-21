angular.module("refugeeapp")
    .controller("donateController", function($scope, apiSvc){
        $scope.donations = [];
        function list(){
            apiSvc.get("donate").then(function(response){
                $scope.donations = response.data.objects;
            });
        }
        list();
        $scope.remove = function(donate){
            apiSvc.remove("donate", donate.id).then(function(response){
                list();
            });
        };
    });

