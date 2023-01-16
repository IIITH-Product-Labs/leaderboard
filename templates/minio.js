var Minio = require(["minio"]);
            var minioClient = new Minio.Client({
                endPoint: 'canvas.iiit.ac.in',
                useSSL: false,
                accessKey: 'minioadmin',
                secretKey: 'Minio@0710'
            });

            var minioBucket = 'leaderboard'
export {minioClient, minioBucket}