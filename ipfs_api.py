import shutil
import nft_storage
from nft_storage.api import nft_storage_api
from nft_storage.model.error_response import ErrorResponse
from nft_storage.model.upload_response import UploadResponse
from nft_storage.model.unauthorized_error_response import UnauthorizedErrorResponse
from nft_storage.model.forbidden_error_response import ForbiddenErrorResponse
import ipfsApi
import os
import json
import requests
import streamlit as st



class IPFSApi:
    def __init__(self):
        pass

    def ipfs_add(self, certi_path):
        api = ipfsapi.Client(host='https://ipfs.infura.io', port=5001)
        res = api.add(certi_path)
        return res

    def ipfs_get(self, record):
        ipfs_url = 'https://gateway.ipfs.io/ipfs/{}'.format(record[0].get('ipfs_hash'))
        st.image(ipfs_url)
        st.write(ipfs_url)
        req = requests.get(ipfs_url, stream=True)
        if os.path.exists('tmp/'):
            shutil.rmtree('tmp/')
        os.makedirs('tmp/')
        file = 'tmp/{}.png'.format(record[0].get('ipfs_hash'))
        with open(file, 'wb') as f:
            shutil.copyfileobj(req.raw, f)
        return ipfs_url

    def nft_port_minting(self,record,wallet_address,ipfs_url):
        try:
            query_params = {
                "chain": "rinkeby",
                "name": "NFT_Name",
                "description": "NFT_Description",
                "mint_to_address": wallet_address
            }
            file = 'tmp/{}.png'.format(record[0].get('ipfs_hash'))
            # file = 'tmp/QmdmzjiWH9F5qWs3FbmqrvnnX5cXdVyEq3v1PN8QdLXbq2.png'

            response = requests.post(
                "https://api.nftport.xyz/v0/mints/easy/files",
                headers={"Authorization": "f6ce3372-a928-4947-8f50-87649f60cee2"},
                                           
                params=query_params,
                files={"file": file}
            )
            res_data = []
            if response.status_code == 200:
                res_data = json.loads(response.content.decode())
                res_data['file_url'] = ipfs_url
                res_data['description'] = 'Certificate metadata verification'
                res_data['name'] = 'MetaData'
                return res_data
            else:
                st.error('Failed to Minting with file')
                return res_data
        except Exception as e:
            print('Got error while upload file to ntf porting :{}'.format(str(e)))
            st.error('Failed to Minting with file')

    # def upload_metadata_to_ipfs(self, data, ipfs_url):
    #     # response_meta = requests.post(
    #     #     "https://api.nftport.xyz/v0/metadata",
    #     #     headers={"Authorization": "f6ce3372-a928-4947-8f50-87649f60cee2"},
    #     #     data=json.dumps(data)
    #     # )
    #     response_meta = requests.post(
    #         "https://api.estuary.tech/content/add",
    #         headers={"Authorization": "Bearer ESTb4e2b39a-6435-4a5a-9a84-6f34df047ad3ARY"},
    #         data=json.dumps(data)
    #     )
    #     print('code',response_meta)
    #     print('con',response_meta.content)
    #     if response_meta.status_code == 200:
    #         meta_url = json.loads(response_meta.content.decode()) \
    #             .get('metadata_uri')
    #         output_data = {
    #             'contract_address': data.get('contract_address'),
    #             'transaction_hash': data.get('transaction_hash'),
    #             'transaction_external_url': data.get('transaction_external_url'),
    #             'mint_to_address': data.get('mint_to_address'),
    #             'ipfs_url': ipfs_url,
    #             'metadata_url': meta_url
    #         }
    #         st.subheader('NTF and IPFS Paths')
    #         st.json(output_data)
    #     else:
    #         st.error('Failed to upload metadata to IPFS')

    # NFT Storage IPFS

    def nft_storage_store(self,file_name):
        # Defining the host is optional and defaults to https://api.nft.storage
        # See configuration.py for a list of all supported configuration parameters.
        configuration = nft_storage.Configuration(
            host="https://api.nft.storage"
        )

        configuration = nft_storage.Configuration(
            access_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDE0RkY4NTU4MzVGMDYwZDBCRTk0ZWQyOTBjNTdiODE1YTE5MjQxNUQiLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTY1NzU2OTU4ODQxOSwibmFtZSI6Ik1BTklESUxMUyJ9.idaK-qJVyOb8WKP1cD0yddE8UJX4zRpBKtX-QqN49fU'
        )
        with nft_storage.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = nft_storage_api.NFTStorageAPI(api_client)
            body = open(file_name, 'rb')  # file_type |


            # example passing only required values which don't have defaults set
            try:
                # Store a file
                api_response = api_instance.store(body, _check_return_type=False)
                return (api_response)
            except nft_storage.ApiException as e:
                st.info("Exception when calling NFTStorageAPI->store: %s\n" % e)

    def get_nft_storage(self,cid_):
        configuration = nft_storage.Configuration(
            host="https://api.nft.storage"
        )
        configuration = nft_storage.Configuration(
            access_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDE0RkY4NTU4MzVGMDYwZDBCRTk0ZWQyOTBjNTdiODE1YTE5MjQxNUQiLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTY1NzU2OTU4ODQxOSwibmFtZSI6Ik1BTklESUxMUyJ9.idaK-qJVyOb8WKP1cD0yddE8UJX4zRpBKtX-QqN49fU'
        )

        with nft_storage.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = nft_storage_api.NFTStorageAPI(api_client)
            cid = cid_  # str | CID for the NFT

            # example passing only required values which don't have defaults set
            try:
                # Get information for the stored file CID
                api_response = api_instance.status(cid, _check_return_type=False)
                return (api_response)
            except nft_storage.ApiException as e:
                print("Exception when calling NFTStorageAPI->status: %s\n" % e)