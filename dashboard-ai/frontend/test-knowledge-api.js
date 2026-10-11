/**
 * Quick test script to verify Knowledge Base API connectivity
 * Run: node test-knowledge-api.js
 */

const axios = require('axios')

const API_URL = 'http://localhost:8000/api'

async function testKnowledgeBaseAPI() {
    console.log('='.repeat(70))
    console.log('KNOWLEDGE BASE API CONNECTIVITY TEST')
    console.log('='.repeat(70))

    try {
        // Test 1: List Knowledge Bases
        console.log('\n[1/3] Testing GET /knowledge-bases...')
        const listResponse = await axios.get(`${API_URL}/knowledge-bases`)
        console.log(`✅ Status: ${listResponse.status}`)
        console.log(`   Knowledge Bases: ${listResponse.data.items.length}`)

        // Test 2: Create Knowledge Base
        console.log('\n[2/3] Testing POST /knowledge-bases...')
        const createResponse = await axios.post(`${API_URL}/knowledge-bases`, {
            name: 'Frontend Test KB',
            description: 'Created from frontend test script'
        })
        console.log(`✅ Status: ${createResponse.status}`)
        console.log(`   Created KB ID: ${createResponse.data.id}`)
        const testKbId = createResponse.data.id

        // Test 3: Delete Knowledge Base
        console.log('\n[3/3] Testing DELETE /knowledge-bases/{id}...')
        const deleteResponse = await axios.delete(`${API_URL}/knowledge-bases/${testKbId}`)
        console.log(`✅ Status: ${deleteResponse.status}`)
        console.log(`   KB deleted successfully`)

        console.log('\n' + '='.repeat(70))
        console.log('✅ ALL TESTS PASSED')
        console.log('Backend API is ready for frontend connection')
        console.log('='.repeat(70))

    } catch (error) {
        console.error('\n❌ TEST FAILED')
        console.error(`Error: ${error.message}`)
        if (error.response) {
            console.error(`Status: ${error.response.status}`)
            console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`)
        } else {
            console.error('Backend may not be running at http://localhost:8000')
            console.error('Start backend with: cd backend && .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload')
        }
        process.exit(1)
    }
}

testKnowledgeBaseAPI()
