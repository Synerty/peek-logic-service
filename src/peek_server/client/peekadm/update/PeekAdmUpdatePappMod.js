'use strict';


// -------------------------- Placeholder Module -----------------------
define([
            // Named Depencencies
            "AngFormLoadController",
            // Unnamed Dependencies
            "angular", "jquery", "ng-file-upload"
        ], function (AngFormLoadController) {
            var peekAdmUpdatePappMod = angular.module('peekAdmUpdatePappMod', ['ngFileUpload']);

// ------------- Controller for updating updater
            peekAdmUpdatePappMod.controller('PeekAdmUpdatePappCtrl', ['$scope', 'Upload',
                function ($scope, Upload) {
                    var self = this;

                    self.loader = new AngFormLoadController($scope,
                            {
                                papp: 'platform',
                                key: "peekadm.papp.version.info"
                            }, {
                                objName: 'pappVersions',
                                dataIsArray: true
                            });

                    self.rspGood = function (data, status, headers, config) {
                        $scope.progressPercentage = '';
                        if (data.error) {
                            logError("Peek App Update Failed<br/>" + data.error);
                        } else {
                            self.loader.load();
                            logSuccess("Peek App Update Complete<br/>New version is "
                                    + data.message);
                        }
                    };

                    self.rspBad = function (data, status, headers, config) {
                        $scope.progressPercentage = '';
                        logError("Peek App Update Failed<br/>" + data.error);
                    };

                    $scope.upload = function (files, event, rejectedFiles) {
                        if (rejectedFiles && rejectedFiles.length) {
                            logError(rejectedFiles[0].name + " does not end in .tar.bz2");
                            return;
                        }

                        if (!(files && files.length))
                            return;

                        var file = files[0];
                        Upload.upload({
                            url: '/peek_server.update.papp',
                            file: file
                        }).progress(function (evt) {
                            $scope.progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                        }).success(self.rspGood)
                                .error(self.rspBad);
                    };


                }
            ]);

        }
);



