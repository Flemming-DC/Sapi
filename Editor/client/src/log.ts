import * as fs from "fs"
const path = require('path');

const logfile = path.join(__dirname, '..', '..', 'client.log');
const log = fs.createWriteStream(logfile);

export default {
    write: (message: object | unknown) => {
        if (typeof message === "object") {
            log.write(JSON.stringify(message));
        } else if (typeof message === "boolean") {
            log.write(message.toString());
        } else if (typeof message === "number") { 
            log.write(message.toString());
        } else if (typeof message === "string") { 
            log.write(message.toString());
        } else if (typeof message === "undefined") { 
            log.write("undefined");
        } else { 
            throw new Error("Unrecognized type");
        }
        log.write("\n");
    }
}

