const util = require('util')
const execPromise = util.promisify(require('child_process').exec)

const listPID = (cmd) => {
    return p = new Promise( async (resolve, reject) => {
        try {
            const { stdout, stderr } = await execPromise(cmd)
            if(stderr) reject(stderr);
            else resolve(stdout)
        } catch (error) {
            reject(error)
        }
    })
}
let commandQuery = 'ps -C node -o stime,pid,user:20,%cpu,%mem,comm,args | grep '+process.argv[2]
async function kill() {
	try{
		let pids = await listPID(commandQuery)
		console.log(pids)
		let toLists = pids.split('\n').filter(v=>!v.includes("kill.js")).filter(v=>v).map(v=>v.split(' ').filter(v=>v))
		let mapLists = toLists.map(v=> {return {
			time: v[0],
			pid: v[1],
			user: v[2]
		}}).filter(v=>!v.time.includes(":"))
		for(let i = 0; i < mapLists.length; i++){
			setTimeout( async () => {
    				const { stdout, stderr } = await execPromise('kill -9 '+mapLists[i].pid)
				console.log(stdout, stderr)
			}, i * 500);	
		}
	}catch(e){
		console.error(e)
	}
}
kill()

