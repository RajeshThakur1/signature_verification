const env = "dev";

export const API_URL = (() => {
    switch (env) {
        case 'prod':
            return 'http://34.134.202.30:5000/';

        case 'dev':
            return 'http://34.134.202.30:5000/';

        default:
            return 'http://34.134.202.30:5000/';
    }
})();

